import asyncio
import time

from langchain.agents import AgentState, create_agent
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.types import Command
from mcp.types import TextContent

from models.init_chat_model.init_chat_model_llm import deepseek_llm


class CustomState(AgentState):
    user_id: str  # 用户ID
    last_op_time: str  # 最后操作时间


# 定义拦截器
async def refund_control_interceptor(request: MCPToolCallRequest, handler):
    """
    每次工具调用后记录操作时间；如果调用退款工具，则直接结束 Agent。
    """
    result = await handler(request)

    # MCP Server 当前返回文本内容，将所有文本块拼接成 ToolMessage。
    content = "\n".join(
        item.text
        for item in result.content
        if isinstance(item, TextContent)
    )
    tool_msg = ToolMessage(
        content=content,
        tool_call_id=request.runtime.tool_call_id
    )

    update = {
        "last_op_time": time.strftime(
            "%Y-%m-%d %H:%M:%S",
            time.localtime(),
        ),
        "messages": [tool_msg],
    }

    # 工具名称属于请求对象，CallToolResult 本身没有 name 字段。
    if request.name == "process_refund":
        return Command(update=update, goto="__end__")

    return Command(update=update)


async def main():
    client = MultiServerMCPClient(
        {
            "my_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        },
        tool_interceptors=[refund_control_interceptor]
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        state_schema=CustomState,
        system_prompt="你是电商售后助手"
    )

    result1 = await agent.ainvoke({

        "messages": [{
            "role": "user",
            "content": "给我查询订单ORD-001的状态"
        }], "user_id": "u_001"
    }, )

    print("result1", result1)
    print(result1["messages"][-1].content)
    print(f"用户{result1.get('user_id')},最后操作时间:", result1.get("last_op_time"))
    print("-----------------")

    result2 = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "ORD-002给我退款"}], "user_id": "u_002"})

    print("result2", result2)
    print(result2["messages"][-1].content)
    print(f"用户{result2.get('user_id')},最后操作时间:", result2.get("last_op_time"))


if __name__ == '__main__':
    asyncio.run(main())
