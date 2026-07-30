import json

from fastmcp import FastMCP

mcp = FastMCP("股票分析服务")

# 模拟数据
STOCK_DATA = {
    "APPLE": {"name": "苹果", "price": 198.5},
    "TESLA": {"name": "特斯拉", "price": 245.8},
    "000001": {"name": "平安银行", "price": 12.35},
}


# ============== 股票相关工具 ==============
@mcp.tool()
async def search_stock(keyword: str) -> str:
    """
    搜索股票，支持股票代码或名称模糊匹配

    Args:
        keyword: 股票代码或名称
    Returns:
        股票信息
    """
    results = []
    for code, data in STOCK_DATA.items():
        if keyword.upper() in code.upper() or keyword in data["name"]:
            results.append(f"{code}（{data['name']}）{data['price']}")

    if not results:
        return f"未找到与 '{keyword}' 相关的股票"
    return "找到以下股票：" + "、".join(results)


@mcp.tool()
async def get_quote(symbol: str) -> str:
    """获取指定股票的实时行情"""
    stock = STOCK_DATA.get(symbol.upper())
    if not stock:
        return json.dumps({"error": f"未找到 {symbol}"}, ensure_ascii=False)
    return json.dumps(stock, ensure_ascii=False)


# ============== 股票相关资源 ==============
@mcp.resource("research://methodology", mime_type="text/markdown", description="当前的股票分析方法论")
async def get_methodology():
    """获取公司标准的股票分析方法论"""
    return """
    股票分析框架：
    1.基本面分析：查看公司营收、利润、资产负债表等
    2.技术分析：查看股票价格趋势、成交量等
    3.行业分析：查看所属行业、行业趋势等
    """


# 数据源依然写在外面，作为静态数据
MARKET_DATA = [
    {"sector": "人工智能", "change": "+3.2%", "hot_stocks": ["NVDA", "AMD"]},
    {"sector": "新能源汽车", "change": "+1.8%", "hot_stocks": ["TESLA", "BYD"]},
    {"sector": "金融", "change": "+0.5%", "hot_stocks": ["000001", "601398"]},
]


@mcp.resource("market://overview/{sector}", mime_type="application/json", description="当前股票市场概览")
async def get_market_overview(sector: str):
    """获取当前股票市场概览。
     Args：
        sector: 行业名称
     Returns：
        JSON格式的市场概览
     """
    filtered_data = [data for data in MARKET_DATA if data["sector"] == sector]
    return json.dumps(filtered_data, ensure_ascii=False)


##============== 股票相关prompt ==============
@mcp.prompt()
async def stock_analysis_prompt(stock_name: str):
    """股票分析prompt"""
    return f" 请为股票 {stock_name} 生成分析报告，包括基本面分析、技术分析、行业分析等。"


if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="127.0.0.1",
        port=8000
    )
