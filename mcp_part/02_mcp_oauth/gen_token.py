"""生成 MCP 基础 JWT 认证示例使用的临时公钥和访问 Token。"""

from fastmcp.server.auth.providers.jwt import RSAKeyPair

key_pair = RSAKeyPair.generate()

# 私钥只在当前进程内用于签名，不输出或交给 MCP Client。
public_key = key_pair.public_key


jwt_token = key_pair.create_token(
    # Token 的主体（Agent 名称）。
    subject="my_agent",
    # Server 会同时验证签发方和接收方。
    issuer="my_company_auth_server",
    audience="internal_mcp_server",
    expires_in_seconds=3600,
)

print("将以下配置复制到本地 .env：")
print(f'MCP_OAUTH_JWT_PUBLIC_KEY="{public_key}"')
print(f"MCP_OAUTH_ACCESS_TOKEN={jwt_token}")
