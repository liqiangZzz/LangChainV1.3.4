"""
MCP 拦截器快速开始示例包。

本包使用 HTTP 数学 MCP Server 演示 tool_interceptors 的基础处理流程。

主要文件：

- math_server.py
  提供加法和乘法两个 FastMCP 工具。

- 01_interceptor_demo1.py
  在工具调用前后输出工具名称、参数和请求信息。

- 02_interceptor_demo2.py
  注册两个异步拦截器，观察拦截器按洋葱模型进入和退出的顺序。

运行注意事项：

- 先运行 math_server.py，再运行任一客户端示例。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度。
"""
