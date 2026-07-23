"""
MCP 拦截器读取 Store 示例包。

本包演示在 MCP 工具拦截器中通过 runtime.store 和 runtime.context 获取长期用户偏好，
再把语言、区域和数量限制注入商品搜索工具参数。

主要文件：

- search_server.py
  提供支持 keyword、language、region 和 limit 参数的模拟商品搜索工具。

- interceptor_read_store_demo.py
  使用 InMemoryStore 保存两个用户的偏好，并在调用 search_product 前动态改写参数。

运行注意事项：

- 先启动 search_server.py，再运行 interceptor_read_store_demo.py。
- Store 为进程内存实现，程序退出后数据不会保留。
- 客户端会调用真实 DeepSeek 模型并消耗 API 额度。
"""
