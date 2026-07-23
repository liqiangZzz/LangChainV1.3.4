from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import JWTVerifier

from env_utils import MCP_JWT_PUBLIC_KEY


if not MCP_JWT_PUBLIC_KEY:
    raise RuntimeError("请先配置 MCP_JWT_PUBLIC_KEY")

auth = JWTVerifier(
    public_key=MCP_JWT_PUBLIC_KEY.replace("\\n", "\n"),
    issuer="my_company_auth_server",
    audience="langchain_mcp_examples",
    algorithm="RS256"
)

# 必须把 verifier 绑定到 FastMCP，认证才会真正生效。
mcp = FastMCP("internal_mcp_server", auth=auth)

# 模拟数据
EMPLOYEE_DB = {
    "E001": {"name": "张三", "department": "技术部", "position": "高级工程师"},
    "E002": {"name": "李四", "department": "财务部", "position": "财务经理"},
    "E003": {"name": "王五", "department": "市场部", "position": "市场总监"},
}

BUDGET_DB = {
    "技术部": {"total": 5000000, "used": 3200000, "remaining": 1800000},
    "财务部": {"total": 1500000, "used": 900000, "remaining": 600000},
    "市场部": {"total": 3000000, "used": 2100000, "remaining": 900000},
}


# 定义工具
@mcp.tool()
async def query_employee(employee_id: str):
    """根据员工ID查询员工信息"""
    employee = EMPLOYEE_DB.get(employee_id)
    if not employee:
        return f"员工 {employee_id} 不存在"
    return f"员工信息: 姓名={employee['name']}，部门={employee['department']}，岗位={employee['position']}"

@mcp.tool()
def query_department_budget(department_name: str):
    """查询部门预算"""
    department = BUDGET_DB.get(department_name)
    if not department:
        return f"部门 {department_name} 不存在"
    return f"部门预算: 总预算={department['total']}，已用预算={department['used']}，剩余预算={department['remaining']}"

if __name__ == '__main__':
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
    )
