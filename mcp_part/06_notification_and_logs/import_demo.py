"""
MCP Client 端，导入数据
"""
import asyncio

from langchain.agents import create_agent
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from langchain_mcp_adapters.client import MultiServerMCPClient
from mcp.types import LoggingMessageNotificationParams

from models.init_chat_model.init_chat_model_llm import deepseek_llm


async def my_on_progress(progress: float,
                         total: float,
                         message: str,
                         context: CallbackContext):
    print(
        f"【进度】MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，当前阶段进度：{progress}%，当前处理消息：{message}")



async def my_on_logging_message(params: LoggingMessageNotificationParams,
                                context: CallbackContext):
    print(
        f"【日志】MCP 服务器名称：{context.server_name},当前工具名称：{context.tool_name}，日志级别：{params.level}，日志消息：{params.data.get("msg")}")


async def main():
    client = MultiServerMCPClient(
        {
            "data_server": {
                "transport": "http",
                "url": "http://127.0.0.1:8000/mcp"
            }
        },
        # 自定义回调函数
        callbacks=Callbacks(
            # 自定义进度回调函数
            on_progress=my_on_progress,
            # 自定义日志回调函数
            on_logging_message=my_on_logging_message
        )
    )

    tools = await client.get_tools()

    agent = create_agent(
        model=deepseek_llm,
        tools=tools,
        system_prompt="你是一个数据导入助手，你可以调用 import_data 工具将数据 导入到数据库中",
    )

    result = await agent.ainvoke({"messages": [{"role": "user", "content": "帮我导入 data.zip数据"}]})
    print(result["messages"][-1].content)


if __name__ == '__main__':
    asyncio.run(main())
