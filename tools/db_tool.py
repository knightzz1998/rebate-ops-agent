"""
返利运维 Agent — 数据库只读查询工具

安全规则:
  1. 仅允许 SELECT/WITH/SHOW/EXPLAIN/DESC
  2. 禁止 INSERT/UPDATE/DELETE/DDL
  3. 账号密码从环境变量读取，不写入配置文件

环境变量:
  REBATE_PG_HOST     — PostgreSQL 主机 (默认 10.31.249.150)
  REBATE_PG_PORT     — PostgreSQL 端口 (默认 5432)
  REBATE_PG_USER     — PostgreSQL 用户
  REBATE_PG_PASSWORD — PostgreSQL 密码
  REBATE_PG_DATABASE — PostgreSQL 数据库 (默认 gksk_rebate)
  REBATE_DORIS_HOST  — Doris 主机
  REBATE_DORIS_PORT  — Doris 端口 (默认 9030)
  REBATE_DORIS_USER  — Doris 用户
  REBATE_DORIS_PASSWORD — Doris 密码
"""

import os, re, asyncio

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    HAS_ASYNCPG = False

# 写操作黑名单 — 发现即拒绝
FORBIDDEN_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "MERGE", "UPSERT", "REPLACE",
    "TRUNCATE", "CREATE", "ALTER", "DROP", "RENAME", "GRANT", "REVOKE",
    "CALL", "DO", "COPY",
]

# 允许的首关键字
ALLOWED_STARTS = ["SELECT", "WITH", "SHOW", "EXPLAIN", "DESC", "DESCRIBE"]


def _validate_sql(sql: str) -> tuple[bool, str]:
    """校验 SQL 安全性"""
    stripped = sql.strip()

    # 检查首关键字
    first_word = stripped.split()[0].upper() if stripped else ""
    if first_word not in ALLOWED_STARTS:
        return False, f"禁止的 SQL 类型: {first_word}。仅允许 {ALLOWED_STARTS}"

    # 检查禁止关键字
    upper_sql = stripped.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        pattern = r'\b' + keyword + r'\b'
        if re.search(pattern, upper_sql):
            return False, f"SQL 包含禁止关键字: {keyword}"

    # 检查多语句
    if ";" in stripped.rstrip(";"):
        return False, "禁止执行多条 SQL"

    return True, ""


async def query_postgres(
    sql: str,
    system_code: str = "",
    limit: int = 100,
) -> dict:
    """
    安全执行 PostgreSQL 只读查询

    参数:
        sql: SQL 语句 (仅允许 SELECT)
        system_code: 租户编码，自动设置 search_path (可选)
        limit: 最大返回行数 (默认 100)

    返回:
        {"rows": [...], "columns": [...], "row_count": N, "error": None}
    """
    # 安全校验
    valid, reason = _validate_sql(sql)
    if not valid:
        return {"rows": [], "columns": [], "row_count": 0, "error": reason}

    if not HAS_ASYNCPG:
        return {
            "rows": [], "columns": [], "row_count": 0,
            "error": "缺少 asyncpg 依赖，请执行: pip install asyncpg"
        }

    # 从环境变量读取连接信息
    host = os.getenv("REBATE_PG_HOST", "10.31.249.150")
    port = int(os.getenv("REBATE_PG_PORT", "5432"))
    user = os.getenv("REBATE_PG_USER", "")
    password = os.getenv("REBATE_PG_PASSWORD", "")
    database = os.getenv("REBATE_PG_DATABASE", "gksk_rebate")

    if not user or not password:
        return {
            "rows": [], "columns": [], "row_count": 0,
            "error": "数据库未配置。请设置环境变量: REBATE_PG_USER / REBATE_PG_PASSWORD"
        }

    try:
        conn = await asyncpg.connect(
            host=host, port=port, user=user, password=password,
            database=database, timeout=10,
        )

        # 如果有 system_code，设置 search_path 到对应 schema
        if system_code:
            schema = f"gksk_rebate_account_{system_code}"
            # 只有表名不含 schema 前缀时才自动设置
            await conn.execute(f"SET search_path TO {schema}, public")

        # 自动追加 LIMIT 防止返回过多数据
        if "LIMIT" not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {limit}"

        rows = await conn.fetch(sql)
        columns = list(rows[0].keys()) if rows else []

        result = []
        for row in rows:
            result.append({col: str(row[col]) for col in columns})

        await conn.close()
        return {
            "rows": result,
            "columns": columns,
            "row_count": len(result),
            "error": None,
        }

    except Exception as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": str(e)}


async def query_doris(
    sql: str,
    limit: int = 100,
) -> dict:
    """
    安全执行 Doris 只读查询

    参数:
        sql: SQL 语句 (仅允许 SELECT)
        limit: 最大返回行数 (默认 100)

    返回:
        {"rows": [...], "columns": [...], "row_count": N, "error": None}
    """
    valid, reason = _validate_sql(sql)
    if not valid:
        return {"rows": [], "columns": [], "row_count": 0, "error": reason}

    host = os.getenv("REBATE_DORIS_HOST", "")
    port = int(os.getenv("REBATE_DORIS_PORT", "9030"))
    user = os.getenv("REBATE_DORIS_USER", "")
    password = os.getenv("REBATE_DORIS_PASSWORD", "")

    if not host or not user or not password:
        return {
            "rows": [], "columns": [], "row_count": 0,
            "error": "Doris 未配置。请设置环境变量: REBATE_DORIS_HOST/USER/PASSWORD"
        }

    try:
        import pymysql
        conn = pymysql.connect(
            host=host, port=port, user=user, password=password,
            charset="utf8mb4", connect_timeout=10,
        )
        cursor = conn.cursor()

        if "LIMIT" not in sql.upper():
            sql = f"{sql.rstrip(';')} LIMIT {limit}"

        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = cursor.fetchall()

        result = []
        for row in rows:
            result.append({columns[i]: str(row[i]) for i in range(len(columns))})

        cursor.close()
        conn.close()
        return {
            "rows": result,
            "columns": columns,
            "row_count": len(result),
            "error": None,
        }

    except Exception as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": str(e)}
