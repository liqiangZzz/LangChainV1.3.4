"""
订单MCP 服务端
"""
import asyncio

from fastmcp import FastMCP, Context

mcp = FastMCP("订单服务")

# 仅用于学习的内存数据：服务重启后状态会恢复，不具备持久化能力。
ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "已发货", "amount": 400.0},
    "ORD-003": {"product": "4K显示器", "status": "已签收", "amount": 2499.0},
    "ORD-004": {"product": "鼠标垫", "status": "配送中", "amount": 29.0},
}


# 查询订单服务
@mcp.tool()
async def query_order(order_id: str, caller_id: str, ctx: Context) -> str:
    """
    根据传入的订单id查询订单信息
    Args:
        order_id: 订单id
        caller_id: 操作人id
        ctx: mcp 上下文
    Returns:
        订单信息
    """

    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在"
    return (
        f"订单 {order_id}信息如下："
        f"商品名称 {order['product']}，"
        f"订单金额 ¥{order['amount']}，"
        f"订单状态 {order['status']}，"
        f"操作人 {caller_id}"
    )


# 订单退款
@mcp.tool()
async def refund_order(
    order_id: str,
    reason: str,
    caller_id: str,
    ctx: Context,
) -> str:
    """
    根据传入的订单id退款，刚发货或者配送中的订单不能退款，已签收的订单可以退款，退款成功后订单状态变为已退款
    Args:
        order_id: 订单id
        reason: 退款原因
        caller_id: 操作人id
        ctx: mcp 上下文
    Returns:
        退款结果
    """

    await ctx.info(f"开始处理订单退款请求，订单id: {order_id}")

    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在，操作人 {caller_id}"

    # 先排除所有不可退款状态，让后面的主流程只处理“已签收”订单。
    status = order["status"]
    if status in {"配送中", "已发货"}:
        return f"订单 {order_id} 状态为{status}，不能退款，操作人 {caller_id}"
    if status == "已退款":
        return f"订单 {order_id} 已退款，请勿重复操作，操作人 {caller_id}"
    if status != "已签收":
        return f"订单 {order_id} 状态为{status}，暂不支持退款，操作人 {caller_id}"

    # elicit 会暂停当前 Tool，直到 Client 返回 accept、decline 或 cancel。
    result = await ctx.elicit(
        message=f"当前订单 {order_id} 状态为已签收可以退款，退款原因：{reason}，是否确认退款",
        response_type=["确认退款", "取消退款"],
    )

    # 处理用户拒绝或取消
    if result.action == "decline":
        await ctx.info(f"订单 {order_id} 用户拒绝退款，操作人 {caller_id}")
        return f"订单 {order_id} 用户拒绝退款，操作人 {caller_id}"
    if result.action == "cancel":
        await ctx.info(f"订单 {order_id} 用户取消退款，操作人 {caller_id}")
        return f"订单 {order_id} 用户取消退款，操作人 {caller_id}"

    # 排除 decline 和 cancel 后，action 只可能是 accept。
    if result.data == "取消退款":
        await ctx.info(f"订单 {order_id} 用户取消退款，操作人 {caller_id}")
        return f"订单 {order_id} 用户取消退款，操作人 {caller_id}"

    # response_type 已将另一个选项限定为“确认退款”。
    await ctx.info(f"订单 {order_id} 用户确认退款，操作人 {caller_id}")
    order["status"] = "已退款"
    return (
        f"用户确认退款，退款金额:{order['amount']}，退款原因:{reason}，"
        f"已经成功退款，订单状态已更新为已退款，操作人id:{caller_id}"
    )


# 批量退款
@mcp.tool()
async def batch_refund(
    order_ids: list[str],
    reason: str,
    caller_id: str,
    ctx: Context,
) -> str:
    """
    批量退款
    Args:
        order_ids: 订单id列表
        reason: 退款原因
        caller_id: 操作人id
        ctx: mcp 上下文
    Returns:
        退款结果
    """
    await ctx.info(f"开始处理批量退款请求，订单id列表: {order_ids}")

    # 清理空白并忽略空订单id
    ids = [order_id.strip() for order_id in order_ids if order_id.strip()]
    if not ids:
        return f"订单id列表不能为空，操作人 {caller_id}"

    # 退款成功订单计数
    success_count = 0

    # 订单总数
    total_count = len(ids)

    # total 使用清理后的订单数量，Client 可以据此计算百分比。
    await ctx.report_progress(0, total_count, "开始批量处理订单退款")

    # 遍历订单id列表
    for index, order_id in enumerate(ids, start=1):
        # 模拟处理每个订单的退款耗时
        await asyncio.sleep(1)

        order = ORDERS.get(order_id)
        if not order:
            await ctx.info(f"订单{order_id}退款失败，当前订单不存在，操作人{caller_id}")
        elif order["status"] in {"配送中", "已发货"}:
            await ctx.info(
                f"订单{order_id}退款失败，当前订单状态为"
                f"{order['status']}，不能退款，操作人{caller_id}"
            )
        elif order["status"] == "已退款":
            await ctx.info(f"订单{order_id}退款失败，当前订单已退款，操作人{caller_id}")
        elif order["status"] != "已签收":
            await ctx.info(
                f"订单{order_id}退款失败，暂不支持当前订单状态"
                f"{order['status']}，操作人{caller_id}"
            )
        else:
            # 批量操作仍逐单确认，避免一次确认直接修改多个订单。
            result = await ctx.elicit(
                message=f"当前订单 {order_id} 状态为已签收可以退款，退款原因：{reason}，是否确认退款",
                response_type=["确认退款", "取消退款"],
            )

            if result.action == "decline":
                await ctx.info(f"订单{order_id}退款失败，用户拒绝退款，操作人{caller_id}")
            elif result.action == "cancel":
                await ctx.info(f"订单{order_id}退款失败，用户取消退款，操作人{caller_id}")
            elif result.data == "确认退款":
                await ctx.info(f"订单{order_id}退款成功，操作人{caller_id}")
                success_count += 1
                order["status"] = "已退款"
            else:
                await ctx.info(f"订单{order_id}退款失败，用户取消退款，操作人{caller_id}")

        # 无论本单成功还是失败，都算作已经处理。
        await ctx.report_progress(
            index,
            total_count,
            f"已处理订单 {order_id}",
        )

    return (
        f"批量处理订单退款完成，退款订单id列表:{ids}，"
        f"退款成功个数:{success_count}，"
        f"退款失败个数:{total_count - success_count}，"
        f"操作人id:{caller_id}"
    )


if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8010,
    )
