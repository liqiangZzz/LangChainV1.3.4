"""
通知服务
"""
from fastmcp import FastMCP, Context

mcp = FastMCP("通知服务")


@mcp.tool()
async def send_sms(
    phone: str,
    message: str,
    caller_id: str,
    ctx: Context,
) -> str:
    """
    发送短信
    Args:
        phone: 手机号
        message: 短信内容
        caller_id: 调用者ID
        ctx: Context对象，包含当前请求的上下文信息，如用户信息、请求ID等
    Returns:
        str: 发送结果
    """
    # 这里只模拟发送动作；号码格式由 Agent 侧的 validate_phone 工具演示校验。
    await ctx.info(f"正在发送短信通知到{phone}，内容：{message}")

    return f"短信通知发送成功，手机号：{phone}，内容：{message}，操作人id：{caller_id}"


# ======================= resources 资源：公司退换货政策  =======================
@mcp.resource("company://return_policy", mime_type="text/markdown", description="公司退换货政策")
async def get_return_policy() -> str:
    # Resource 适合提供可直接读取的业务资料；这里返回无额外缩进的 Markdown。
    return (
        "## 退换货政策\n"
        "1. 签收后 7 天内可无理由退货（商品不影响二次销售）\n"
        "2. 质量问题 30 天内可换货，运费商家承担\n"
        "3. 退货时赠品需一并退回\n"
        "4. 退款将在收货确认后 3 个工作日内退回原支付方式"
    )


# ======================= prompt ：提示词模板  =======================
@mcp.prompt
async def refund_response_prompt(order_id: str, amount: str) -> str:
    """
    退款响应提示词
    Args:
        order_id (str): 订单ID
        amount (str): 退款金额
    Returns:
        str: 退款响应提示词
    """
    # Prompt 与 Resource 不同：它接收参数并生成一段可复用的消息模板。
    return (
        f"好的，已为您处理订单 {order_id} 的退款。\n"
        f"退款金额：{amount} 元\n"
        f"预计 3 个工作日内退回原支付方式。\n"
        f"如有疑问可随时联系我们。"
    )


if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8020
    )
