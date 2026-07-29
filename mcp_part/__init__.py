"""
Model Context Protocol（MCP）学习示例包。

本包演示使用 FastMCP 创建服务端工具，并通过 langchain-mcp-adapters 将一个或多个
MCP Server 的能力接入 LangChain Agent。内容覆盖基础通信、JWT 认证、工具调用拦截器、
工具异常处理、通知与日志、Elicitation，以及 Tool、Resource 与 Prompt 的综合使用。

子包说明：

- 01_quick_start
  演示 stdio、HTTP 两种 MCP 通信方式，以及 MultiServerMCPClient 聚合多个服务端工具。

- 02_mcp_oauth
  演示 RSA 密钥和 JWT 的生成、Bearer Token 请求头及 JWTVerifier 配置。

- 03_interceptor
  演示 MCP 工具调用拦截器的日志、组合、运行时上下文注入、Store 读取和状态更新。

- 04_handler_tool_error
  演示 MCP 工具业务异常和瞬时故障的传递，以及 Agent 在限定次数内重试工具调用。

- 05_resources_and_prompt
  演示 MCP Tool、Resource 和 Prompt 在股票研究 Agent 中的职责划分与组合流程。

- 06_notification_and_logs
  演示 MCP Server 日志、进度通知，以及 Client Callbacks 的接收与展示。

- 07_elicitation
  演示工具执行期间由 Server 请求用户补充输入，并处理 accept、decline 和 cancel。

- 08_comprehensive_example
  通过电商售后场景综合演示多 Server、拦截器、状态更新、HITL 和 Elicitation。

运行注意事项：

- 客户端示例会调用真实 DeepSeek 模型并消耗 API 额度。
- 工具异常处理示例可能触发多轮模型和工具重试，额度消耗会相应增加。
- HTTP 示例需要先启动对应 MCP Server，再运行客户端脚本；多个示例默认使用 8000 端口，
  应分别运行，避免端口冲突；售后综合示例单独使用 8010 和 8020 端口。
- Elicitation 和售后综合示例会等待终端输入，需要在交互式终端中运行。
- 股票研究示例使用本地模拟数据，不构成真实行情或投资建议。
- JWT、公钥和访问 Token 示例仅用于本地学习，真实凭据不得提交到仓库。
- 本包的 __init__.py 只提供说明，不导入示例模块。
"""
