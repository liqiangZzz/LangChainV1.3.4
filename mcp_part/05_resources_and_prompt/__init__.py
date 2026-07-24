"""
MCP Tool、Resource 与 Prompt 综合示例包。

本包通过股票研究场景演示 MCP Server 同时提供可调用工具、只读资源和可复用
Prompt，并由客户端将三类能力组合到 LangChain Agent 的一次完整任务中。

主要文件：

- stock_server.py
  提供股票搜索和行情查询工具、股票分析方法论和行业概览资源，以及股票分析
  Prompt 模板；所有股票和市场内容均为本地模拟数据。

- stock_research_client.py
  读取 Resource 构造只读参考上下文，获取服务端 Prompt 作为任务消息，并将 Tool
  注册给 Agent 按需调用，最后生成股票分析报告。

运行注意事项：

- 先启动 stock_server.py，再运行 stock_research_client.py；HTTP 服务默认使用
  8000 端口。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度，运行前需正确配置模型环境变量。
- 示例输出仅用于学习 MCP 能力组合，不构成真实行情数据或投资建议。
- 本包的 __init__.py 只提供说明，不导入示例模块。
"""
