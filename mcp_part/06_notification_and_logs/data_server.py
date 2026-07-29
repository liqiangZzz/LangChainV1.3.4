"""
MCP Server 端
"""
import asyncio

from fastmcp import FastMCP, Context

mcp = FastMCP("数据服务")

# 导入数据的步骤
IMPORT_STAGE = ["解压文件", "校验字段", "写入数据库"]


@mcp.tool()
async def import_data(filename: str, ctx: Context) -> str:
    """导入数据到数据库中
    Args:
        filename: 文件名
        ctx: Context对象，包含当前请求的上下文信息，如用户信息、请求ID等
    Returns:
        str: 导入结果
    """
    total = 100

    # 将日志发送到Client中
    await ctx.debug(f"这是debug日志，开始导入数据 {filename}")
    await ctx.info(f"这是info日志，开始导入数据 {filename}")
    await ctx.warning(f"这是warning日志，开始导入数据 {filename}")
    await ctx.error(f"这是error日志，开始导入数据 {filename}")

    # 将进度条发送到client
    await ctx.report_progress(0, total, "开始导入数据")

    cnt = 0
    for stage in IMPORT_STAGE:
        await ctx.info(f"正在导入数据，当前阶段：{stage}")

        # 模拟每个阶段3秒耗时
        await  asyncio.sleep(3)
        cnt += 25
        await ctx.report_progress(cnt, total, f"正在导入数据，当前阶段：{stage}")

    await ctx.report_progress(100, total, f"导入数据成功！")

    return "全部数据已经导入成功！"


if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000
    )
