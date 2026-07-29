"""
MCP Elicitation 用户补充输入示例包。

本包通过文件导入冲突场景演示 MCP Server 在工具执行期间暂停调用并请求用户选择，
以及 Client 如何处理 accept、decline 和 cancel 三种 Elicitation 结果。

主要文件：

- import_server.py
  提供已有文件查询和文件导入工具；遇到同名文件时通过 ctx.elicit() 请求覆盖、
  跳过或取消导入。

- import_demo.py
  注册命令行 Elicitation 回调，展示服务端提供的选项，并把用户决定返回给
  MCP Server；同时将远程工具接入 LangChain Agent。

运行注意事项：

- 先启动 import_server.py，再运行 import_demo.py；HTTP 服务默认使用 8000 端口。
- 触发同名文件导入时会等待终端输入，需要在交互式终端中运行客户端。
- 文件列表仅保存在服务端内存中，不会创建、覆盖或删除真实文件。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度，运行前需配置模型环境变量。
- 本包的 __init__.py 只提供说明，不导入示例模块。
"""
