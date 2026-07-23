"""
MCP 拦截器注入运行时认证上下文示例包。

本包演示多个 Agent 共用一个 JWT 调用同一 HTTP MCP Server。Agent 在 ainvoke 时传入
认证上下文，拦截器把 Token 写入 Authorization 请求头，服务端使用公钥完成 JWT 验签。

主要文件：

- generate_agent_credentials.py
  为本地示例生成临时 RSA 公钥和一小时有效期的共享 JWT。

- interceptor_context_demo.py
  创建查询和退款两个 Agent，共用 MCP 工具，并从 runtime context 动态注入 JWT。

- order_server.py
  使用 JWTVerifier 保护订单 MCP Server，并从验签后的 sub claim 识别调用主体。

运行注意事项：

- 先生成凭据并将 MCP_JWT_PUBLIC_KEY、MCP_ACCESS_TOKEN 配置到本地 .env。
- 再启动 order_server.py，最后运行 interceptor_context_demo.py。
- 每次重新生成凭据都必须同时更新公钥和 Token；不要混用不同批次的值。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度。
"""
