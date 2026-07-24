import random

from fastmcp import FastMCP
from sqlalchemy.orm import defer

mcp = FastMCP("error_server")

USERS = {"U001": "张三", "U002": "李四", "U003": "王五"}


@mcp.tool()
async def get_user(user_id: str):
    """
     根据用户ID获取用户信息
    """
    if user_id not in USERS:
        raise ValueError(f"用户{user_id} 不存在，请确认ID是否正确")

    return f"用户{user_id}的姓名是：{USERS[user_id]}"


@mcp.tool()
async def search_database(keyword: str):
    """
    根据关键词搜索数据库，返回匹配结果
    Args:
        keyword: 搜索关键词
    Returns:
        匹配结果
    """
    if random.random() < 0.01:
        return f"关键词{keyword}的搜索结果找到了10条数据"
    raise RuntimeError("网络波动了，数据库连接超时，重试一下即可")


if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
