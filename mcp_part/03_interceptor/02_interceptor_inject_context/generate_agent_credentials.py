"""生成多个 Agent 共用的临时 RSA 公钥和 JWT。

仅用于本地学习。生产环境应由独立认证服务保管私钥并签发 Token。
"""

from fastmcp.server.auth.providers.jwt import RSAKeyPair


# JWT 的签发方和接收方必须与 MCP Server 中 JWTVerifier 的配置完全一致。
ISSUER = "my_company_auth_server"
AUDIENCE = "langchain_mcp_examples"


def create_token(
    key_pair: RSAKeyPair,
    subject: str,
) -> str:
    """使用 RSA 私钥签发一个有效期为一小时的共享 Agent Token。"""
    return key_pair.create_token(
        # sub 用于标识通过认证的调用主体。
        subject=subject,
        issuer=ISSUER,
        audience=AUDIENCE,
        expires_in_seconds=24 * 60 * 60,
    )


# 本地示例每次运行都会生成新的密钥对，旧公钥和旧 Token 将不再匹配。
# 私钥只保留在 key_pair 内存中，不输出给 Client 或 MCP Server。
key_pair = RSAKeyPair.generate()

# MCP Server 只需要公钥验签；多个 Agent 共用同一个 JWT。
escaped_public_key = key_pair.public_key
access_token = create_token(
    key_pair,
    subject="shared_agent",
)

# 将这两个值作为一组复制，不能混用不同运行批次产生的公钥和 Token。
print("将以下配置复制到本地 .env：")
print(f'MCP_JWT_PUBLIC_KEY="{escaped_public_key}"')
print(f"MCP_ACCESS_TOKEN={access_token}")
