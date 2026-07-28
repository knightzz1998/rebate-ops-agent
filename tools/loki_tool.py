"""
返利运维 Agent — Loki 日志查询工具

封装已有的 query_rebate_loki.py，提供 AgentScope 友好的接口
"""

import sys, os, time, argparse
from pathlib import Path
from typing import Optional

REBATE_SKILL_PATH = os.path.expanduser(
    "~/.config/opencode/rebate-superpowers/skills/rebate-log-query"
)
sys.path.insert(0, os.path.join(REBATE_SKILL_PATH, "scripts"))

from query_rebate_loki import (
    load_env_config,
    resolve_session,
    fetch_logs,
    parse_time_to_ns,
    flatten_lines,
    GrafanaQueryError,
    DEV_DEFAULT_BASE_URL,
    DEV_DEFAULT_LOKI_UID,
    DEFAULT_ORG_ID,
)

CONFIG_FILE = os.path.join(REBATE_SKILL_PATH, "references", "log-env-config.json")


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
        {"total": N, "logs": [...], "error": None}
    """
    try:
        # 加载配置
        env_config = load_env_config(CONFIG_FILE, env)
        base_url = env_config.get("base_url", DEV_DEFAULT_BASE_URL)
        datasource_uid = env_config.get("loki_uid", DEV_DEFAULT_LOKI_UID)
        org_id = env_config.get("org_id", DEFAULT_ORG_ID)

        # 构建 Loki 表达式
        if app and contains:
            expr = f'{{app="{app}"}} |= "{contains}"'
        elif app:
            expr = f'{{app="{app}"}}'
        elif contains:
            expr = f'{{app=~".+"}} |= "{contains}"'
        else:
            expr = '{app=~".+"}'

        # 时间转换
        now_ts = time.time()
        start_ns = parse_time_to_ns(time_from, now_ts)
        end_ns = parse_time_to_ns(time_to, now_ts)

        # 获取 session (自动处理缓存和刷新)
        fake_args = argparse.Namespace(
            env=env,
            session=None,
            username=None,
            password=None,
            session_cache_file=os.path.join(
                REBATE_SKILL_PATH, "references", ".grafana-session-cache.json"
            ),
            config_file=CONFIG_FILE,
        )
        env_upper = env.upper()
        session = resolve_session(fake_args, env_upper, env_config, base_url)

        # 查询 Loki
        raw_data = fetch_logs(
            base_url=base_url,
            datasource_uid=datasource_uid,
            org_id=org_id,
            session=session,
            expr=expr,
            start_ns=start_ns,
            end_ns=end_ns,
            limit=limit,
            direction="backward",
        )

        # 解析结果
        lines = flatten_lines(raw_data)
        total = len(lines)
        logs = []
        for timestamp_ns, labels, line in lines[:limit]:
            timestamp_sec = timestamp_ns / 1_000_000_000
            timestamp_str = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(timestamp_sec)
            )
            logs.append({
                "timestamp": timestamp_str,
                "app": labels.get("app", ""),
                "line": line[:500],  # 截断超长日志
            })

        return {"total": total, "logs": logs, "error": None}

    except GrafanaQueryError as e:
        return {
            "total": 0, "logs": [],
            "error": f"查询失败 (HTTP {e.status_code}): {e.body[:200]}",
        }
    except Exception as e:
        return {"total": 0, "logs": [], "error": f"工具异常: {str(e)}"}
