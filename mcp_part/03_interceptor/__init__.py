"""
MCP 工具调用拦截器示例包。

本包围绕 MultiServerMCPClient 的 tool_interceptors 展示 MCP 工具执行前后的扩展方式，
包括日志记录、多个拦截器组合、请求改写、运行时信息读取和 Command 状态更新。

子包说明：

- 01_interceptor_quick_start
  演示单个日志拦截器和多个拦截器的洋葱式执行顺序。

- 02_interceptor_inject_context
  演示从 Agent runtime context 读取共享 JWT，并动态注入 MCP HTTP 请求头。

- 03_interceptor_read_store
  演示从 runtime.store 读取用户偏好并覆盖 MCP 工具参数。

- 04_interceptor_update_state
  演示把 MCP 结果转换为 ToolMessage，通过 Command 更新自定义 AgentState 并结束执行。

运行注意事项：

- 每个客户端示例运行前都要先启动同目录的 MCP Server。
- 各 HTTP Server 默认占用 8000 端口，应按专题分别运行。
- 客户端会调用真实 DeepSeek 模型，工具调用可能产生多轮请求和额外额度消耗。
"""
