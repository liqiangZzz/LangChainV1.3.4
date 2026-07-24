"""生成 MCP 认证示例共用的临时 RSA 公钥和 JWT。"""

from fastmcp.server.auth.providers.jwt import RSAKeyPair

key_pair = RSAKeyPair.generate()

# 私钥仅在当前进程中用于签名，不输出或交给 MCP Client。
public_key = key_pair.public_key
jwt_token = key_pair.create_token(
    # 两个认证示例共用相同的 issuer 和 audience。
    # Token的主体(Agent 名称)
    subject="my_agent",
    # 签发方的标识,Server验证token的时候会验证
    issuer="my_company_auth_server",
    # 接收方的标识,Server验证token的时候会验证
    audience="langchain_mcp_examples",
    # Token 的有效期
    expires_in_seconds=24 * 60 * 60,
)

print("将以下配置复制到本地 .env：")
print(f'MCP_JWT_PUBLIC_KEY="{public_key}"')
print(f"MCP_ACCESS_TOKEN={jwt_token}")
