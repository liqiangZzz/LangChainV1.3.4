from dataclasses import dataclass

from langchain.agents import AgentState, create_agent
from langchain.agents.middleware import before_model
from langchain_core.tools import tool
from langgraph.runtime import Runtime

from models.init_chat_model.init_chat_model_llm import deepseek_llm


@dataclass
class Context:
    user_name: str


# 获取当前系统时间
@tool
def get_current_time():
    """获取当前系统时间。"""
    from datetime import datetime
    return f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"


@before_model
def auth_gate(state: AgentState, runtime: Runtime) -> dict | None:
    """
    鉴权网关，用于拦截未授权的请求。
    """

    #  获取运行时信息
    server_info = runtime.server_info
    #  获取执行信息
    exec_info = runtime.execution_info

    print("server_info", server_info)
    print("exec_info", exec_info)
    return None


agent = create_agent(
    model=deepseek_llm,
    tools=[get_current_time],
    middleware=[auth_gate],
    context_schema=Context,
    system_prompt="你是一个助手，可以帮助用户查询时间。",
)

print("=" * 50)
config = {"configurable": {"thread_id": "123"}}
result = agent.invoke({  # type: ignore
    "messages": [{
        "role": "user",
        "content": "当前时间是多少？"
    }]}, config=config, context=Context(user_name="张三"))

print(result["messages"][-1].content)
