"""
返利运维 Agent — 数据库只读查询工具

安全策略:
  1. 所有查询必须经过 db-readonly-query SKILL 的安全校验
  2. 仅允许 SELECT / WITH / SHOW / EXPLAIN / DESCRIBE
  3. 禁止 INSERT / UPDATE / DELETE / DDL / 多语句
  4. 账号密码从环境变量读取
"""

import os, sys, tempfile, configparser, asyncio
from typing import Optional

SKILL_PATH = os.path.expanduser(
    "~/.config/opencode/rebate-superpowers/skills/db-readonly-query"
)
sys.path.insert(0, os.path.join(SKILL_PATH, "scripts"))

from query_postgres_readonly import (
    validate_sql,
    run_query,
    resolve_schema,
    PostgresConfig,
)


async def query_postgres(
    sql: str,
    system_code: str = "",
    limit: int = 100,
) -> dict:
    """
    通过 db-readonly-query SKILL 安全执行 PostgreSQL 只读查询

    参数:
        sql: SQL 语句 (仅允许 SELECT)
        system_code: 租户编码，自动映射到对应 schema
        limit: 最大返回行数 (默认 100)

    返回:
        {"rows": [...], "columns": [...], "row_count": N, "error": None}
    """
    # 1. 从环境变量读取连接信息
    host = os.getenv("REBATE_PG_HOST", "")
    port = os.getenv("REBATE_PG_PORT", "5432")
    user = os.getenv("REBATE_PG_USER", "")
    password = os.getenv("REBATE_PG_PASSWORD", "")
    database = os.getenv("REBATE_PG_DATABASE", "gksk_rebate")

    if not host or not user or not password:
        return {
            "rows": [], "columns": [], "row_count": 0,
            "error": "数据库未配置。请设置环境变量: REBATE_PG_HOST/USER/PASSWORD"
        }

    # 2. 自动追加 LIMIT
    if "LIMIT" not in sql.upper() and "limit" not in sql:
        sql = f"{sql.rstrip(';')} LIMIT {limit}"

    # 3. SKILL 安全校验 (继承所有黑名单/白名单规则)
    try:
        validated_sql = validate_sql(sql, allow_explain_analyze=False)
    except SystemExit as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": f"SQL校验失败 (exit {e.code})"}
    except Exception as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": f"SQL校验异常: {str(e)}"}

    # 4. 解析 schema
    schema_map_path = os.path.join(SKILL_PATH, "config", "system_code_schema_map.json")
    schema = resolve_schema(system_code, schema_map_path) if system_code else None

    # 5. 执行查询
    config = PostgresConfig(
        host=host,
        port=int(port),
        database=database,
        user=user,
        password=password,
        sslmode="prefer",
        connect_timeout=5,
        statement_timeout_ms=30000,
        psql_bin="psql",
    )

    try:
        # 重定向 stdout 捕获 run_query 的输出
        import io
        old_stdout = sys.stdout
        sys.stdout = capture = io.StringIO()

        exit_code = run_query(config, validated_sql, "csv", schema)
        sys.stdout = old_stdout

        if exit_code != 0:
            return {"rows": [], "columns": [], "row_count": 0, "error": capture.getvalue()[:200]}

        # 解析 CSV 输出
        csv_output = capture.getvalue().strip()
        if not csv_output:
            return {"rows": [], "columns": [], "row_count": 0, "error": None}

        lines = csv_output.split("\n")
        if len(lines) < 2:
            return {"rows": [], "columns": [], "row_count": 0, "error": None}

        columns = [c.strip() for c in lines[0].split(",")]
        rows = []
        for line in lines[1:]:
            values = [v.strip() for v in line.split(",")]
            rows.append({columns[i]: values[i] if i < len(values) else "" for i in range(len(columns))})

        return {"rows": rows, "columns": columns, "row_count": len(rows), "error": None}

    except Exception as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": str(e)}


async def query_doris(
    sql: str,
    limit: int = 100,
) -> dict:
    """
    通过 db-readonly-query SKILL 安全执行 Doris 只读查询

    参数:
        sql: SQL 语句 (仅允许 SELECT)
        limit: 最大返回行数 (默认 100)

    返回:
        {"rows": [...], "columns": [...], "row_count": N, "error": None}
    """
    host = os.getenv("REBATE_DORIS_HOST", "")
    port = os.getenv("REBATE_DORIS_PORT", "9030")
    user = os.getenv("REBATE_DORIS_USER", "")
    password = os.getenv("REBATE_DORIS_PASSWORD", "")

    if not host or not user or not password:
        return {
            "rows": [], "columns": [], "row_count": 0,
            "error": "Doris 未配置。请设置环境变量: REBATE_DORIS_HOST/USER/PASSWORD"
        }

    if "LIMIT" not in sql.upper() and "limit" not in sql:
        sql = f"{sql.rstrip(';')} LIMIT {limit}"

    # Doris 也走 PostgreSQL 的安全校验 (规则一致)
    try:
        validate_sql(sql, allow_explain_analyze=False)
    except SystemExit as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": f"SQL校验失败 (exit {e.code})"}
    except Exception as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": f"SQL校验异常: {str(e)}"}

    try:
        import pymysql
        conn = pymysql.connect(
            host=host, port=int(port), user=user, password=password,
            charset="utf8mb4", connect_timeout=10,
        )
        cursor = conn.cursor()
        cursor.execute(sql)

        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        db_rows = cursor.fetchall()
        result = [{columns[i]: str(db_rows[j][i]) for i in range(len(columns))} for j in range(len(db_rows))]

        cursor.close()
        conn.close()
        return {"rows": result, "columns": columns, "row_count": len(result), "error": None}

    except Exception as e:
        return {"rows": [], "columns": [], "row_count": 0, "error": str(e)}
