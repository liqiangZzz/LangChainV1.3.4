import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from env_utils import MCP_ACCESS_TOKEN
from models.init_chat_model.init_chat_model_llm import deepseek_llm


async def main():
    if not MCP_ACCESS_TOKEN:
        raise RuntimeError("请先配置 MCP_ACCESS_TOKEN")

    client = MultiServerMCPClient(
        {
            "internal_mcp_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp",
                "headers": {
                    "Authorization": f"Bearer {MCP_ACCESS_TOKEN}"
                }
            }
        }
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
    )

    result1 = await agent.ainvoke({"messages": [{"role": "user", "content": "查询一下E002员工信息"}]})
    print(result1["messages"][-1].content)

    result2 = await agent.ainvoke({"messages": [{"role": "user", "content": "查询一下财务部的预算"}]})
    print(result2["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())
