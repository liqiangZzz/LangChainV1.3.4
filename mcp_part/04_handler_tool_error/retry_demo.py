import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

from models.init_chat_model.init_chat_model_llm import deepseek_llm


async def main():
    client = MultiServerMCPClient(
        {
            "remote_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        },
        #  是否处理工具错误,默认为 True
        # handle_tool_errors=False
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是一个助手，调用search_database工具查询数据库中的信息，如果出现错误，请重试最多5次，如果依然失败，请返回错误信息"
    )
    # result = await agent.ainvoke({"messages": [{"role": "user", "content": "帮我查询U999用户信息"}]})
    # print(f"result:", result)

    result =  await agent.ainvoke({"messages": [{"role": "user", "content": "帮我去数据库查询下大模型关键词相关的信息"}]})
    print(f"result:", result)

if __name__ == '__main__':
    asyncio.run(main())
