"""
Model Context Protocol（MCP）学习示例包。

本包演示使用 FastMCP 创建服务端工具，并通过 langchain-mcp-adapters 将一个或多个
MCP Server 的工具接入 LangChain Agent。内容覆盖基础通信、JWT 认证和工具调用拦截器。

子包说明：

- 01_quick_start
  演示 stdio、HTTP 两种 MCP 通信方式，以及 MultiServerMCPClient 聚合多个服务端工具。

- 02_mcp_oauth
  演示 RSA 密钥和 JWT 的生成、Bearer Token 请求头及 JWTVerifier 配置。

- 03_interceptor
  演示 MCP 工具调用拦截器的日志、组合、运行时上下文注入、Store 读取和状态更新。

运行注意事项：

- 客户端示例会调用真实 DeepSeek 模型并消耗 API 额度。
- HTTP 示例需要先启动对应 MCP Server，再运行客户端脚本；多个示例默认使用 8000 端口，
  应分别运行，避免端口冲突。
- JWT、公钥和访问 Token 示例仅用于本地学习，真实凭据不得提交到仓库。
- 本包的 __init__.py 只提供说明，不导入示例模块。
"""
