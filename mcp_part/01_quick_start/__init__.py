"""
MCP 快速开始示例包。

本包演示创建本地 stdio 数学服务和 HTTP 天气服务，再使用 MultiServerMCPClient
统一加载工具并交给 LangChain Agent 调用。

主要文件：

- math_server.py
  使用 FastMCP 提供加法和乘法工具，由客户端以 stdio 子进程方式启动。

- weather_server.py
  使用 FastMCP 在 HTTP 路径 /mcp-a 提供模拟城市天气查询工具。

- mcp_demo.py
  同时连接数学和天气两个 MCP Server，将远程工具转换为 LangChain 工具并创建 Agent。

运行注意事项：

- 先启动 weather_server.py，再运行 mcp_demo.py；数学服务由客户端自动启动。
- Agent 调用会访问真实 DeepSeek 模型并消耗 API 额度，天气结果为本地模拟数据。
"""
