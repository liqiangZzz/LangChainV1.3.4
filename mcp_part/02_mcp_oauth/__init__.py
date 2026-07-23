"""
MCP JWT 认证示例包。

本包演示为 HTTP MCP 调用准备 RSA/JWT 凭据，在客户端请求头中携带 Bearer Token，
并在服务端配置 JWTVerifier 校验签名、签发方和接收方。

主要文件：

- gen_token.py
  生成临时 RSA 密钥对和一小时有效期的 JWT，输出可复制到 .env 的公钥和访问 Token。

- mcp_server.py
  定义员工和部门预算工具，并把 JWTVerifier 绑定到 FastMCP Server。

- mcp_client.py
  通过 MultiServerMCPClient 连接 HTTP MCP Server，在请求头中传递 JWT 后创建 Agent。

运行注意事项：

- gen_token.py 输出包含访问 Token，只适合本地学习，不要保存到日志或提交仓库。
- 公钥、JWT 的 issuer、audience 必须成套匹配；示例 Token 过期后需要重新生成。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度。
"""
