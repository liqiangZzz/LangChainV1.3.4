"""
MCP Client  售后助手
"""
import asyncio
import operator
import time
from dataclasses import dataclass
from typing import Annotated

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from mcp.shared.context import RequestContext
from mcp.types import (
    ElicitRequestParams,
    ElicitResult,
    LoggingMessageNotificationParams,
    TextContent,
)

from models.init_chat_model.init_chat_model_llm import deepseek_llm


# 运行时上下文用于保存“本次调用是谁发起的”，不会由模型生成。
@dataclass
class CustomContext:
    user_id: str
    user_name: str


class CustomState(AgentState):
    # operator.add 让每次工具调用产生的审计列表追加到已有列表，而不是覆盖。
    audit_log: Annotated[list[str], operator.add]


# 本地工具
@tool
def validate_phone(phone: str) -> str:
    """验证手机号是否合法"""
    if len(phone) == 11 and phone.isdigit() and phone.startswith("1"):
        return "手机号格式正确"
    return "手机号格式错误，手机号是11位数字，且以1开头。"


# ========================= 拦截器 =========================
# 认证拦截器，用于注入用户信息
async def auth_inject(request: MCPToolCallRequest, handler):
    """
        从自定义上下文中获取用户信息，然后注入到 MCP Server 工具中
    """
    runtime = request.runtime
    ctx = runtime.context

    user_id = ctx.user_id
    user_name = ctx.user_name

    # request.override() 不修改原请求；caller_id 会在真正调用 MCP Tool 前注入。
    return await handler(request.override(
        args={**request.args, "caller_id": f"{user_id}-{user_name}"},
    ))


# 审计拦截器，用于记录用户操作
async def audit_log(request: MCPToolCallRequest, handler):
    """
        审计拦截器，用于记录用户操作
    """
    runtime = request.runtime
    ctx = runtime.context

    user_id = ctx.user_id
    user_name = ctx.user_name

    result = await handler(request)

    # handler 返回 MCP CallToolResult；Agent 状态中的 messages 则需要
    # LangChain ToolMessage，因此先提取 MCP TextContent 再完成类型转换。
    content = "\n".join(
        item.text
        for item in result.content
        if isinstance(item, TextContent)
    )

    tool_msg = ToolMessage(
        content=content,
        tool_call_id=request.runtime.tool_call_id
    )

    # reducer 接收的是 list[str]，所以单条日志也必须包装成列表再更新。
    logs = (
        f"[{time.strftime('%H:%M:%S')}] "
        f"{user_id}-{user_name} -> {request.name}:{request.args}"
    )

    return Command(
        update={
            "messages": [tool_msg],
            "audit_log": [logs],
        }
    )


# ========================= 回调函数 =========================
# 进度回调，用于打印当前进度
async def on_progress(
        progress: float,
        total: float | None,
        message: str | None,
        context: CallbackContext):
    """
    进度回调
    Args:
        progress: 进度
        total: 总进度
        message: 消息
        context: 上下文
    """

    if total:
        progress_text = f"{(progress / total) * 100:.2f}%"
    else:
        # MCP 允许不提供 total，此时只能展示当前进度值。
        progress_text = str(progress)

    print(
        f"【进度】MCP 服务器名称：{context.server_name},"
        f"当前工具名称：{context.tool_name}，"
        f"当前阶段进度：{progress_text}，当前处理消息：{message}"
    )


# 日志回调，用于打印日志消息
async def on_logging_message(
        params: LoggingMessageNotificationParams,
        context: CallbackContext):
    """
    日志回调
    Args:
        params: 日志参数
        context: 上下文
    """
    if isinstance(params.data, dict):
        log_message = params.data.get("msg", params.data)
    else:
        log_message = params.data

    print(
        f"【日志】MCP 服务器名称：{context.server_name},"
        f"当前工具名称：{context.tool_name}，"
        f"日志级别：{params.level}，日志消息：{log_message}"
    )


#  elicitation 回调，用于处理 elicitation 请求
async def on_elicitation(
        mcp_context: RequestContext,
        params: ElicitRequestParams,
        context: CallbackContext) -> ElicitResult:
    """
    elicitation 回调
    Args:
        mcp_context:  MCP 请求上下文
        params: elicitation 请求参数
        context: 上下文
    """
    message = params.message

    print(f"【系统询问】-{message}")

    # order_server 使用字符串列表作为 response_type，FastMCP 会把它转换为
    # properties.value.enum；使用 get 逐层读取可避免其他 schema 触发 KeyError。
    options = (
        params.requestedSchema
        .get("properties", {})
        .get("value", {})
        .get("enum", [])
    )

    # 如果 Server 没有提供选项，Client 无法继续收集用户输入，取消本次交互。
    if not options:
        print("服务端没有提供可选项，本次交互已取消")
        return ElicitResult(action="cancel")

    # 打印可选选项
    for index, option in enumerate(options, 1):
        print(f"{index}. {option}")

    # 用户输入
    while True:
        input_prompt = (
            f"请输入编号（1-{len(options)}），"
            "d 表示拒绝回答，c 表示取消交互："
        )

        # input() 是同步阻塞函数，通过 asyncio.to_thread() 放到独立线程执行，
        # 避免阻塞当前异步事件循环。
        raw_input = await asyncio.to_thread(input, input_prompt)
        selected_input = raw_input.strip().lower()

        # decline 表示用户明确拒绝回答 Server 发起的询问。
        if selected_input == "d":
            return ElicitResult(action="decline")

        # cancel 表示用户取消整个 elicitation 交互。
        if selected_input == "c":
            return ElicitResult(action="cancel")

        # 业务选项使用数字编号选择，先检查输入是否为数字。
        if selected_input.isdigit():
            selected_index = int(selected_input)

            # 用户看到的编号从 1 开始，列表下标从 0 开始。
            if 1 <= selected_index <= len(options):
                selected_option = options[selected_index - 1]

                # accept 表示用户接受本次询问并提交数据。
                # content 必须符合 requestedSchema，这里的 value 保存具体业务选项。
                return ElicitResult(
                    action="accept",
                    content={"value": selected_option},
                )

            print(
                f"输入无效，请输入 1-{len(options)} 之间的编号，"
                "或者输入 d、c"
            )
            continue

        print(
            f"输入无效，请输入 1-{len(options)} 之间的编号，"
            "或者输入 d、c"
        )


async def main():
    # 1.创建MCP Client
    client = MultiServerMCPClient(
        {
            "order_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8010/mcp",
            },
            "notify_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8020/mcp",
            }
        },
        # 拦截器按洋葱模型执行：auth_inject 是外层，audit_log 能看到注入后的参数。
        tool_interceptors=[auth_inject, audit_log],
        callbacks=Callbacks(
            on_progress=on_progress,
            on_logging_message=on_logging_message,
            on_elicitation=on_elicitation
        )
    )

    # 2.获取工具列表
    tools = await client.get_tools()

    # 3. Resource 转成 Blob，Prompt 转成 LangChain Message。
    blobs = await client.get_resources(
        "notify_server",
        uris=["company://return_policy"]
    )
    policy_text = "\n".join(b.as_string() for b in blobs)

    msgs = await client.get_prompt(
        "notify_server",
        "refund_response_prompt",
        arguments={"order_id": "{退款订单号}", "amount": "{退款金额}"}
    )
    prompt = msgs[0].content

    agent = create_agent(
        model=deepseek_llm,
        tools=tools + [validate_phone],
        checkpointer=InMemorySaver(),
        state_schema=CustomState,
        context_schema=CustomContext,
        middleware=[
            HumanInTheLoopMiddleware(
                # 这里是 Agent 调用工具前的人工审批；批准后，退款工具内部还会
                # 通过 MCP Elicitation 收集具体的“确认退款/取消退款”选项。
                interrupt_on={
                    "refund_order": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "请确认是否同意退款"
                    },
                    "batch_refund": {
                        "allowed_decisions": ["approve", "reject"],
                        "description": "请确认是否同意批量退款"
                    }
                }
            )
        ],
        system_prompt=f"""你是电商售后客服助手。
               工作流程：
               1. 查询订单时调用 query_order。如果订单不存在，直接告知用户不要重试。
               2. 退款时先查询订单确认状态和金额。
               3. 退款成功后询问用户是否需要短信通知。如果要通知，先调用 validate_phone 校验手机号，再用 send_sms 发送。
               4. 涉及退换货政策问题时，参考以下政策：
               {policy_text}
               5. 回复退款结果时，参考以下模板：
               {prompt}
           """
    )

    ctx = CustomContext(user_id="zhangsan", user_name="张三")
    config = {"configurable": {"thread_id": "session001"}}

    print("="*70)
    print("电商智能售后客服")
    print("=" * 70)

    while True:
        user_input = input("用户: ").strip()

        if not user_input:
            continue

        if user_input =="exit":
            print("退出程序")
            break

        # version="v2" 返回 GraphOutput，可通过 value 和 interrupts 分别读取
        # 当前状态与待处理的人工审批。
        result = await agent.ainvoke(
            {
                "messages": [{
                    "role": "user",
                    "content": user_input,
                }]
            },
            config=config,
            context=ctx,
            version="v2",
        )

        result = await handle_interrupts(result, agent, config, ctx)

        # 输出最终回复
        final_msg = result.value["messages"][-1].content
        print("[助手]：", final_msg)

        # 获取审计记录
        audit_logs = result.value.get("audit_log", [])
        print("审计记录：")
        for log in audit_logs:
            print(log)


def get_action_args(action_request: dict) -> dict:
    """兼容 HITL 请求中使用 arguments 或 args 保存参数的版本差异。"""
    return action_request.get(
        "arguments",
        action_request.get("args", {}),
    )


# 中断处理方法
async def handle_interrupts(result, agent, config, ctx):
    """
    处理一轮或多轮中断，直到 Agent 不再触发中断为止。

    返回值：最终的 GraphOutput（此时 result.interrupts 为空）
    """
    while result.interrupts:
        #
        interrupt_data = result.interrupts[0].value
        action_requests = interrupt_data["action_requests"]
        review_configs = interrupt_data["review_configs"]

        print("中断数据：", interrupt_data)
        print("操作请求:",action_requests)
        print("审查配置:",review_configs)


        # 展示所有待人工介入操作
        print(f"\n{'─' * 60}")
        print(f" Agent中断 —— {len(action_requests)} 个操作需要人工介入")
        print(f"{'─' * 60}")

        for i, req in enumerate(action_requests):
            cfg = review_configs[i]
            request_args = get_action_args(req)
            print(f"\n  [{i}] 工具名称 : {req['name']}")
            print(f"      参数    : {request_args}")
            print(f"      允许决策 : {cfg['allowed_decisions']}")

        # 逐个收集决策（决策顺序 == action_requests 顺序）
        decisions = []

        print(f"\n{'·' * 40}")
        print("请按顺序对以上操作做出决策：")
        print(f"{'·' * 40}")

        for i, req in enumerate(action_requests):
            allowed = review_configs[i]["allowed_decisions"]
            request_args = get_action_args(req)

            print(f"\n 操作 [{i}] {req['name']}")
            # 展示当前参数供人工介入参考
            if request_args:
                for k, v in request_args.items():
                    print(f"     参数: {k} = {v}")

            # 可用的决策类型及说明
            hint_map = {
                "approve": "批准，按原参数执行工具",
                "edit": "修改参数后执行工具",
                "reject": "拒绝执行，附带反馈说明",
                "respond": "跳过工具执行，直接返回人工回复",
            }
            print("     可选操作：")
            for a in allowed:
                print(f"       > {a} — {hint_map.get(a)}")

            # 等待有效输入
            while True:
                decision = input(f"      >>> 输入操作 ({'/'.join(allowed)}): ").strip().lower()
                if decision in allowed:
                    break
                print(f"      无效输入，该操作只允许: {allowed}")

            # 根据决策类型构建决策对象
            if decision == "approve":
                decisions.append({"type": "approve"})
                print(f"      已批准 —— 工具将按原参数执行")

            elif decision == "edit":
                print(f"      请输入修改后的参数（直接回车保留原值）：")
                new_args = {}
                for k, v in request_args.items():
                    new_val = input(f"         {k} [原值: {str(v)}]: ").strip()
                    if new_val == "":
                        new_args[k] = v  # 保留原值
                    else:
                        # 直接使用用户输入的字符串
                        new_args[k] = new_val
                decisions.append({
                    "type": "edit",
                    "edited_action": {"name": req["name"], "args": new_args},
                })
                print(f"      已修改参数: {new_args}")

            elif decision == "reject":
                reason = input(f"      请输入拒绝原因: ").strip()
                if not reason:
                    reason = "操作被人工拒绝"
                decisions.append({"type": "reject", "message": reason})
                print(f"      已拒绝:{reason}")

            elif decision == "respond":
                reply = input(f"      请输入回复内容: ").strip()
                if not reply:
                    reply = "已确认，没有补充信息。"
                decisions.append({"type": "respond", "message": reply})
                print(f"      已回复:{reply}")

        # 提交决策，恢复执行
        print(f"\n{'─' * 60}")
        print(f"提交决策列表:{decisions}")
        print(f"{'─' * 60}")

        # 使用同一个 thread_id 和 context 恢复刚才暂停的 Agent 执行。
        result = await agent.ainvoke(
            Command(resume={"decisions": decisions}),
            config=config,
            context=ctx,
            version="v2",
        )

    return result


if __name__ == '__main__':
    asyncio.run(main())
