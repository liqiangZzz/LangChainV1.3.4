"""
Runtime 与上下文工程示例包。

本包围绕 LangChain Agent 的 Runtime（运行时）和上下文工程展开，重点演示
如何通过 context_schema 传入调用级别的上下文数据，以及如何在工具、
middleware 和 dynamic_prompt 中访问 Runtime 提供的 state、store、
context、execution_info 等能力。

学习主线：

1. 定义 context_schema，在 invoke 时传入上下文，在工具中通过 ToolRuntime 读取。
2. 在工具中使用 runtime.store 读取长期记忆（LangGraph Store）。
3. 在 middleware 中通过 Runtime 访问上下文和 state，实现动态提示词和日志记录。
4. 通过 runtime.execution_info 和 runtime.server_info 获取执行元数据。
5. 综合利用 State、Store、Runtime Context 三个数据源动态生成系统提示词。
6. 使用 wrap_model_call middleware 根据上下文动态注入消息内容。
7. 使用 wrap_model_call middleware 根据用户角色动态过滤可用工具。

context 与 state 的区别：

- context 是本次 invoke/stream 传入的运行时上下文，只在当前调用中有效，
  不会被 checkpointer 自动保存。适合传递当前用户身份、角色、环境、租户等
  请求级别参数。通过 context_schema 声明类型，在工具和 middleware 中通过
  runtime.context 访问。
- state 是 Agent 的会话状态，会被 checkpointer 按 thread_id 持久化保存。
  默认包含 messages，也可以通过 state_schema 扩展业务字段。适合保存后续
  多轮对话还要继续使用的信息。

Runtime 的两种形态：

- ToolRuntime：在 @tool 函数中通过参数 `runtime: ToolRuntime[Context]` 注入，
  包含 context、state、store、tool_call_id、config、stream_writer 等属性。
- Runtime：在 middleware 和 graph 节点中通过参数 `runtime: Runtime[Context]`
  注入，包含 context、state、store、server_info、execution_info 等属性。

主要文件：

- 01_runtime_basic.py
  演示 context_schema 的基础用法：定义 dataclass 上下文，在 invoke 时传入，
  在工具中通过 ToolRuntime 读取用户名和角色。

- 02_runtime_in_tools.py
  演示在工具中通过 runtime.store 访问 LangGraph Store（长期记忆），
  读取用户邮件偏好设置并结合上下文信息生成回复。

- 03_runtime_in_middleware.py
  演示在 middleware 中通过 Runtime 访问上下文：dynamic_prompt 根据用户角色
  动态生成系统提示词，before_model / after_model 记录调用日志。

- 04_runtime_execution_info.py
  演示通过 runtime.execution_info 和 runtime.server_info 获取执行元数据，
  包括线程标识、运行 ID 等信息，可用于审计和调试。

- 05_context_engineering_system_prompt.py
  综合示例：结合 State（消息数量）、Store（用户偏好）和 Runtime Context
  （用户角色、部署环境）三个数据源，动态生成系统提示词。

- 06_context_engineering_messages.py
  演示使用 wrap_model_call middleware，根据 Runtime Context 中的 file_path
  读取文件内容并注入到消息列表，实现上下文感知的消息增强。

- 07_context_engineering_tools.py
  演示使用 wrap_model_call middleware，根据 Runtime Context 中的用户角色
  动态过滤可用工具列表，实现基于权限的工具访问控制。

运行方式：

- 请从项目根目录使用模块方式运行，例如：
  python -m runtime_and_context_engineering.01_runtime_basic
  python -m runtime_and_context_engineering.03_runtime_in_middleware
  python -m runtime_and_context_engineering.05_context_engineering_system_prompt
  python -m runtime_and_context_engineering.07_context_engineering_tools

运行注意事项：

- 多数示例会在模块顶层调用真实模型，运行前注意 API 额度、网络和环境变量配置。
- 本包不在 `__init__.py` 中导入示例模块，避免导入包时触发真实 LLM 请求。
"""
