"""
返利运维 Agent — Loki 日志查询工具

封装已有的 query_rebate_loki.py，提供 AgentScope 友好的接口
"""

import sys, os, json
from pathlib import Path
from typing import Optional

# 把返利日志查询脚本路径加入 sys.path
REBATE_SKILL_PATH = os.path.expanduser(
    "~/.config/opencode/rebate-superpowers/skills/rebate-log-query"
)
sys.path.insert(0, os.path.join(REBATE_SKILL_PATH, "scripts"))

from query_rebate_loki import (
    build_loki_url,
    fetch_loki_logs,
    resolve_session,
    resolve_config,
    GrafanaQueryError,
)


async def query_logs(
    env: str = "dev",
    app: Optional[str] = None,
    contains: Optional[str] = None,
    time_from: str = "now-15m",
    time_to: str = "now",
    limit: int = 100,
) -> dict:
    """
    查询返利系统 Grafana Loki 日志

    参数:
        env: 环境 (dev / sit / prod)
        app: 应用名，如 gksk-rebate-system
        contains: 日志关键词
        time_from: 开始时间 (默认 now-15m)
        time_to: 结束时间 (默认 now)
        limit: 最大返回条数 (默认 100)

    返回:
        {
            "total": 命中条数,
            "logs": [{"timestamp": "...", "line": "..."}, ...],
            "error": None  # 如有错误则不为 None
        }
    """
    try:
        # 1. 加载配置
        config = resolve_config(env)

        # 2. 构建 Loki 查询 URL
        params = {
            "limit": limit,
            "direction": "backward",
        }

        # 构建 query 表达式
        if app and contains:
            params["query"] = f'{{app="{app}"}} |= "{contains}"'
        elif app:
            params["query"] = f'{{app="{app}"}}'
        elif contains:
            params["query"] = f'{{app=~".+"}} |= "{contains}"'
        else:
            params["query"] = '{app=~".+"}'

        params["start"] = time_from
        params["end"] = time_to

        # 3. 查询
        session = resolve_session(env, config)
        raw_data = fetch_loki_logs(
            base_url=config["base_url"],
            loki_uid=config.get("loki_uid", ""),
            org_id=config.get("org_id", "1"),
            session=session,
            params=params,
        )

        # 4. 解析结果
        results = raw_data.get("data", {}).get("result", [])
        total = 0
        logs = []

        for stream in results:
            for timestamp_ns, line in stream.get("values", []):
                total += 1
                timestamp = timestamp_ns[:19] if len(timestamp_ns) > 19 else timestamp_ns
                logs.append({
                    "timestamp": timestamp,
                    "line": line,
                })

        return {
            "total": total,
            "logs": logs[:limit],
            "error": None,
        }

    except GrafanaQueryError as e:
        return {
            "total": 0,
            "logs": [],
            "error": f"查询失败 (HTTP {e.status_code}): {e.body[:200]}",
        }
    except Exception as e:
        return {
            "total": 0,
            "logs": [],
            "error": f"工具异常: {str(e)}",
        }
