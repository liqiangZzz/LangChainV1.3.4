"""
MCP 电商售后综合示例包。

本包通过订单退款和短信通知场景，组合 MCP Tool、Resource、Prompt、日志、进度、
Elicitation、工具调用拦截器、自定义 Agent 状态和 Human-in-the-loop 审批。

主要文件：

- order_server.py
  提供订单查询、单笔退款和批量退款工具；退款时根据订单状态执行业务校验，
  通过 Elicitation 逐单确认，并在批量处理中发送日志和进度。

- notify_server.py
  提供模拟短信通知工具、公司退换货政策 Resource 和退款回复 Prompt。

- after_sale_agent.py
  聚合订单与通知两个 MCP Server，注入调用者信息、记录审计日志，并组合本地手机号
  校验工具、Agent Human-in-the-loop 审批和 MCP Elicitation 交互。

运行注意事项：

- 先分别启动 order_server.py（8010 端口）和 notify_server.py（8020 端口），
  再运行 after_sale_agent.py。
- Agent 审批和 MCP Elicitation 都会等待终端输入，需要在交互式终端中运行客户端。
- 客户端会调用真实 DeepSeek 模型，工具选择、多轮对话和中断恢复会增加 API 额度消耗。
- 订单和短信均为本地模拟数据；订单状态保存在服务端内存中，重启后会恢复。
- 本包的 __init__.py 只提供说明，不导入示例模块。
"""
