import asyncio
from dataclasses import dataclass

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langgraph.store.memory import InMemoryStore

from models.init_chat_model.init_chat_model_llm import deepseek_llm


@dataclass
class CustomerContext:
    user_id: str  # 用户id


# 定义拦截器
async def person_info_inject_interceptor(request: MCPToolCallRequest, handler):
    """
    获取 store 中的用户信息，作为参数传递给工具
    """

    runtime = request.runtime
    store = runtime.store
    user_id = runtime.context.user_id

    prefs = store.get(("user_prefs",), user_id)

    # 如果用户有偏好，并且当前调用的工具是 search_product，则注入参数
    if prefs and request.name == "search_product":
        language = prefs.value.get("language", "zh")
        region = prefs.value.get("region", "CN")
        limit = prefs.value.get("limit", 10)
        # 调用原始的工具调用逻辑
        return await handler(request.override(
            # 将原来的参数拿过来,然后添加新的参数
            args={**request.args, "language": language, "region": region, "limit": limit}
        ))
    return await handler(request)


async def main():
    # 构建长期记忆
    store = InMemoryStore()
    store.put(("user_prefs",), "u_001", {"language": "en", "region": "US", "limit": 2})
    store.put(("user_prefs",), "u_002", {"language": "zh", "region": "CN", "limit": 5})

    client = MultiServerMCPClient(
        {
            "my_match_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        },
        # 传入拦截器列表
        tool_interceptors=[person_info_inject_interceptor]
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        store=store,
        context_schema=CustomerContext,
        system_prompt="你是一个商品搜索助手，根据用户输入的商品名称，调用search_product搜索商品信息"
    )

    result = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "给我搜一下耳机"
        }]
    }, context=CustomerContext(user_id="u_001"))

    print(result["messages"][-1].content)

    print("-----------------")

    result2 = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "给我搜索耳机"
        }]
    }, context=CustomerContext(user_id="u_002"))

    print(result2["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())
