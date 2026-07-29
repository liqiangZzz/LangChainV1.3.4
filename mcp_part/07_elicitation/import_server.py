"""
MCP Server 导入文件服务
"""
from fastmcp import FastMCP, Context

mcp = FastMCP("import_server")

# 模拟服务端已经存在的文件，用于触发文件冲突确认。
EXISTING_FILE = ["data.zip"]


@mcp.tool()
async def list_existing_files() -> str:
    """返回服务端当前已经存在的文件。"""
    return f"当前存在文件：{EXISTING_FILE}"


@mcp.tool()
async def import_file(file_name: str, ctx: Context) -> str:
    """
    导入文件
    Args:
        file_name: 文件名
        ctx: Context对象，包含当前请求的上下文信息，如用户信息、请求ID等
    Returns:
        str: 导入结果
    """

    if file_name in EXISTING_FILE:
        # 暂停当前工具调用，并向 MCP Client 发起 elicitation 请求。
        # Client 的 on_elicitation 回调返回结果后，await 才会继续执行。
        result = await ctx.elicit(
            message=f"文件 {file_name} 已存在，请确认操作！",
            response_type=["覆盖文件", "跳过该文件", "取消导入"]
        )


        # action 表示用户对本次询问的整体处理结果。
        if result.action == "accept":
            # 该输出属于 MCP Server，应在启动 import_server 的终端中查看。
            print("=======================", result)

            # response_type 是单选列表，因此用户选择保存在 result.data 中。
            choice = result.data
            if choice == "覆盖文件":
                return f"文件 {file_name} 已经覆盖并成功导入"
            elif choice == "跳过该文件":
                return f"跳过文件 {file_name}"
            elif choice == "取消导入":
                return f"用户取消导入文件 {file_name}"

            # 正常情况下，MCP 会根据 response_type 校验 Client 返回的数据，
            # 因此不会进入这个分支。这里保留明确返回，便于学习完整流程。
            return f"无法识别用户选择：{choice}"
        elif result.action == "decline":
            return "用户拒绝导入"
        elif result.action == "cancel":
            return "用户取消导入"

    # 文件不存在时不需要 elicitation，直接模拟执行导入并更新服务端文件列表。
    EXISTING_FILE.append(file_name)
    return f"文件 {file_name} 已经成功导入"


if __name__ == '__main__':
    # 使用 Streamable HTTP 启动 MCP Server，客户端连接地址为
    # http://127.0.0.1:8000/mcp。
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
