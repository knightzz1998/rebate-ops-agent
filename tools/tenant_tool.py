"""
返利运维 Agent — 租户信息查询工具

用途: 查询租户编码 ↔ 租户名称 的映射关系
数据来源: 数据库查询 (生产/测试环境)
"""

import os, asyncio

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

# 内置已知映射 (从 skill system_code_schema_map.json 推导)
KNOWN_TENANTS = {
    "1228": "国控广州",
    "1224": "国控浙江",
    "1220": "国药控股",
    "1014": "国控北京",
    "1109": "国控江苏",
    "1110": "国控河南",
    "1114": "国控山东",
    "1115": "国控湖北",
    "1116": "国控湖南",
    "1119": "国控福建",
    "1141": "国控安徽",
    "1143": "国控江西",
    "1164": "国控四川",
    "1168": "国控陕西",
    "1170": "国控山西",
    "1173": "国控河北",
    "1180": "国控吉林",
    "1181": "国控辽宁",
    "1183": "国控黑龙江",
    "1184": "国控内蒙古",
    "1196": "国控新疆",
    "1198": "国控甘肃",
    "1006": "国控宁夏",
    "1010": "国控青海",
    "1226": "国控云南",
    "1229": "国控贵州",
    "1235": "国控海南",
    "1239": "国控广西",
    "1240": "国控西藏",
}


async def lookup_tenant(keyword: str) -> dict:
    """
    根据关键词查询租户信息

    参数:
        keyword: 租户编码(如1228) 或 租户名称关键词(如"浙江"、"广州")

    返回:
        {"found": [...], "count": N, "error": None}
    """
    results = []

    # 1. 先从本地已知映射查找
    for code, name in KNOWN_TENANTS.items():
        if keyword.lower() in code or keyword.lower() in name.lower() or keyword.lower() in name:
            results.append({"code": code, "name": name, "source": "本地"})

    # 2. 尝试从数据库查真实租户名称
    if HAS_ASYNCPG:
        host = os.getenv("REBATE_PG_HOST", "10.31.249.150")
        port = int(os.getenv("REBATE_PG_PORT", "5432"))
        user = os.getenv("REBATE_PG_USER", "")
        password = os.getenv("REBATE_PG_PASSWORD", "")
        database = os.getenv("REBATE_PG_DATABASE", "gksk_rebate")

        if user and password:
            try:
                conn = await asyncpg.connect(
                    host=host, port=port, user=user,
                    password=password, database=database, timeout=5,
                )

                # 从 tenant 表查真实名称
                sql = f"""
                    SELECT tenant_id, tenant_code, tenant_name
                    FROM tenant_info
                    WHERE tenant_code LIKE '%{keyword}%'
                       OR tenant_name LIKE '%{keyword}%'
                    LIMIT 20
                """
                rows = await conn.fetch(sql)
                for row in rows:
                    results.append({
                        "code": str(row["tenant_code"]),
                        "name": row["tenant_name"] or "",
                        "source": "数据库",
                    })
                await conn.close()
            except Exception:
                pass  # 数据库不可用，用本地数据即可

    if results:
        return {"found": results, "count": len(results), "error": None}
    else:
        return {
            "found": [], "count": 0,
            "error": f"未找到与 '{keyword}' 匹配的租户",
        }


def list_all_tenants() -> dict:
    """列出所有已知租户"""
    tenants = [
        {"code": code, "name": name}
        for code, name in sorted(KNOWN_TENANTS.items(), key=lambda x: x[1])
    ]
    return {"found": tenants, "count": len(tenants), "error": None}
