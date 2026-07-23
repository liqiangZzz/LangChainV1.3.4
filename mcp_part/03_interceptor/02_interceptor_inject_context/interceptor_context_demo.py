import asyncio
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

from env_utils import MCP_ACCESS_TOKEN
from models.init_chat_model.init_chat_model_llm import deepseek_llm


@dataclass
class AgentAuthContext:
    """Agent 单次运行时使用的认证上下文，不会成为 MCP 工具参数。"""

    # agent_name 仅用于本地错误提示，服务端身份以 JWT 的 sub 为准。
    agent_name: str
    # 多个 Agent 当前共用同一个 JWT，后续也可以按 Agent 替换为不同 Token。
    access_token: str


async def auth_inject_interceptor(request: MCPToolCallRequest, handler):
    """把当前 Agent 的 JWT 动态放入 MCP HTTP 请求头。"""
    # runtime.context 来自 agent.ainvoke(..., context=...)。
    context = request.runtime.context
    if not context.access_token:
        raise ValueError(f"Agent {context.agent_name} 缺少 MCP access token")

    # Token 通过 HTTP Header 传输，不暴露成模型可生成或修改的工具参数。
    return await handler(
        request.override(
            headers={"Authorization": f"Bearer {context.access_token}"},
        )
    )


async def main():
    if not MCP_ACCESS_TOKEN:
        raise RuntimeError("请先配置 MCP_ACCESS_TOKEN")

    client = MultiServerMCPClient(
        {
            "order_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp",
                # get_tools() 发生在 ainvoke() 之前，还没有 AgentAuthContext，
                # 所以工具发现阶段先在连接配置中使用同一个共享 Token。
                "headers": {
                    "Authorization": f"Bearer {MCP_ACCESS_TOKEN}"
                },
            }
        },
        tool_interceptors=[auth_inject_interceptor],
    )

    # 两个 Agent 复用同一份 MCP 工具定义和同一个 MCP Client。
    tools = await client.get_tools()

    query_agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        context_schema=AgentAuthContext,
        system_prompt="你是订单查询 Agent，只负责查询订单。",
    )

    refund_agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        context_schema=AgentAuthContext,
        system_prompt="你是订单退款 Agent，只负责提交退款申请。",
    )

    # 调用工具时，拦截器会读取这里传入的运行时认证上下文。
    query_result = await query_agent.ainvoke(
        {"messages": [{"role": "user", "content": "查询订单 ORD-001 信息"}]},
        context=AgentAuthContext(
            agent_name="query_agent",
            access_token=MCP_ACCESS_TOKEN,
        ),
    )
    print(query_result["messages"][-1].content)

    # 当前示例不区分 Agent 权限，因此退款 Agent 复用同一个 Token。
    refund_result = await refund_agent.ainvoke(
        {
            "messages": [
                {"role": "user", "content": "订单 ORD-003 退款，原因是买错了"}
            ]
        },
        context=AgentAuthContext(
            agent_name="refund_agent",
            access_token=MCP_ACCESS_TOKEN,
        ),
    )
    print(refund_result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
