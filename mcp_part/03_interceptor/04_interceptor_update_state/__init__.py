"""
MCP 拦截器更新 Agent 状态示例包。

本包演示拦截器处理 MCP CallToolResult，将文本内容转换为 ToolMessage，并通过
LangGraph Command 更新自定义 AgentState；退款工具完成后可直接跳转到结束节点。

主要文件：

- order_server.py
  提供订单状态查询和退款处理两个 FastMCP 工具。

- command_demo.py
  扩展 AgentState 保存用户 ID 和最后操作时间，并由拦截器返回 Command 更新状态。

运行注意事项：

- 先启动 order_server.py，再运行 command_demo.py。
- 退款工具会修改 MCP Server 进程内的模拟订单状态，重启服务后恢复初始数据。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度。
"""
