from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token

from env_utils import MCP_JWT_PUBLIC_KEY


if not MCP_JWT_PUBLIC_KEY:
    raise RuntimeError("请先配置 MCP_JWT_PUBLIC_KEY")

# MCP Server 只持有公钥，用它校验 JWT 签名、签发方和接收方。
# 私钥不应出现在 MCP Server 或 Agent 代码中。
auth = JWTVerifier(
    # 同时兼容 .env 中保存的真实换行和字面量 \n。
    public_key=MCP_JWT_PUBLIC_KEY.replace("\\n", "\n"),
    issuer="my_company_auth_server",
    audience="langchain_mcp_examples",
    algorithm="RS256",
)

# 绑定 auth 后，未携带有效 Bearer Token 的 MCP 请求会在调用工具前被拒绝。
mcp = FastMCP("OrderServer", auth=auth)

ORDERS = {
    "ORD-001": {"product": "无线耳机", "status": "已签收", "amount": 299.0},
    "ORD-002": {"product": "机械键盘", "status": "待发货", "amount": 599.0},
    "ORD-003": {"product": "显示器", "status": "已完成", "amount": 1299.0},
}


def get_authenticated_agent_id() -> str:
    """返回通过 MCP Server 验签后的 Agent 身份。"""
    # get_access_token() 获取的是 JWTVerifier 已经验证过的访问令牌。
    access_token = get_access_token()
    if access_token is None:
        raise PermissionError("未通过 MCP 身份认证")

    # 使用标准 sub claim 识别调用主体，不信任 Client 额外传入的身份参数。
    agent_id = access_token.claims.get("sub")
    if not isinstance(agent_id, str) or not agent_id:
        raise PermissionError("JWT 中缺少有效的 sub")
    return agent_id


@mcp.tool
def query_order(order_id: str) -> str:
    """查询指定订单。"""
    # 每个业务工具都从认证信息中取得真实调用身份。
    caller_id = get_authenticated_agent_id()
    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在"
    return (
        f"订单 {order_id} "
        f"商品： {order['product']} "
        f"状态： {order['status']} "
        f"金额： {order['amount']}，"
        f"操作人： {caller_id}"
    )


@mcp.tool
def submit_refund(order_id: str, reason: str) -> str:
    """提交退款申请。"""
    # 当前示例只做统一身份认证，暂不区分查询和退款权限。
    caller_id = get_authenticated_agent_id()
    order = ORDERS.get(order_id)
    if not order:
        return f"订单 {order_id} 不存在，无法提交退款申请"
    if order["status"] == "已签收":
        return f"订单 {order_id} 已签收，无法提交退款申请"

    return (
        f"订单 {order_id} 已提交退款申请，退款原因：{reason}，"
        f"退款金额：{order['amount']}，"
        f"退款人：{caller_id}"
    )


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000,
    )
