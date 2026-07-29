"""
MCP 通知、日志与进度回调示例包。

本包演示 MCP Server 在工具执行期间向 Client 发送不同级别的日志和进度通知，
以及 MultiServerMCPClient 如何通过 Callbacks 接收并展示这些事件。

主要文件：

- data_server.py
  提供模拟数据导入工具，在解压、字段校验和写入数据库等阶段发送日志与进度通知。

- import_demo.py
  注册进度和日志回调，将远程导入工具接入 LangChain Agent，并输出服务端通知。

运行注意事项：

- 先启动 data_server.py，再运行 import_demo.py；HTTP 服务默认使用 8000 端口。
- 数据导入仅为延时模拟，不会读取文件或写入真实数据库。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度，运行前需配置模型环境变量。
- 本包的 __init__.py 只提供说明，不导入示例模块。
"""
