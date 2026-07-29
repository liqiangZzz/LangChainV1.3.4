"""
MCP Client 端，导入数据
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.client.streamable_http import RequestContext
from mcp.types import LoggingMessageNotificationParams, ElicitRequestParams, ElicitResult

from models.init_chat_model.init_chat_model_llm import deepseek_llm


async def on_progress(progress: float,
                      total: float,
                      message: str,
                      context: CallbackContext):
    """接收 MCP Server 在工具执行期间发送的进度通知。"""
    print(
        f"[进度] MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，当前阶段进度：{progress}%，当前处理消息：{message}")


async def on_logging_message(params: LoggingMessageNotificationParams,
                             context: CallbackContext):
    """接收 MCP Server 主动发送的结构化日志。"""
    print(
        f"[日志] MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，日志级别：{params.level}，日志消息：{params.data.get('msg')}")


async def on_elicitation(mcp_context: RequestContext,
                         params: ElicitRequestParams,
                         context: CallbackContext, ) -> ElicitResult:
    """
    处理 MCP Server 发起的 elicitation 请求。

    当前示例通过命令行展示服务端提供的选项，并把用户选择返回给 MCP Server。
    真实项目中也可以在这里接入前端确认框或人工审批页面。
    """
    # print("mcp_context:",mcp_context)
    # print("params:",params)
    # print("context:",context)

    # message 是 Server 调用 ctx.elicit() 时传入的提示信息。
    message = params.message
    print(f"【系统询问】-{message}")

    # requestedSchema 由 Server 的 response_type 自动生成。
    requested_schema = params.requestedSchema

    # 当前 response_type 是字符串列表，所以选项位于 value.enum。
    options = requested_schema["properties"]["value"]["enum"]

    # 如果 Server 没有提供选项，Client 无法继续收集用户输入，取消本次交互。
    if not options:
        print("服务端没有提供可选项，本次交互已取消")
        return ElicitResult(action="cancel")

    # 按照 1、2、3 的编号展示 Server 提供的业务选项。
    for option_index, option_text in enumerate(options, start=1):
        print(f"{option_index}. {option_text}")

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




async def main():
    # callbacks 会绑定到 MCP 会话，负责接收 Server 的通知和 elicitation 请求。
    client = MultiServerMCPClient(
        {
            "import_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        },
        callbacks=Callbacks(
            on_progress=on_progress,
            on_logging_message=on_logging_message,
            on_elicitation=on_elicitation
        )
    )

    # 将远程 MCP 工具转换成 LangChain Agent 可以调用的 Tool。
    tools = await client.get_tools()

    # Agent 决定何时调用 import_file；工具中的 ctx.elicit() 则由
    # MultiServerMCPClient 配置的 on_elicitation 回调响应。
    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是一个数据导入助手，你可以调用 import_file 工具将数据 导入到数据库中",
    )

    # result1 = await agent.ainvoke({"messages": [{"role": "user", "content": "将 data.zip 给我导入"}]})
    # print("result1:", result1)
    # print(result1["messages"][-1].content)

    result2 = await agent.ainvoke({"messages": [{"role": "user", "content": "查看已经存在的文件"}]})
    print(result2["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())
