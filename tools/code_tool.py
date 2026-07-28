"""
返利运维 Agent — 代码仓库查询工具

能力:
  1. 按关键词搜索代码
  2. 查看文件内容
  3. 列出仓库
  4. 查看 Git 历史
"""

import os, subprocess, asyncio
from typing import Optional

# 代码仓库根目录
REBATE_CODE_ROOT = os.path.expanduser("~/Code/work/rebate")

KNOWN_REPOS = [
    "gksk-rebate-system",
    "gksk-rebate-account",
    "gksk-rebate-calculate",
    "gksk-rebate-aggregate",
    "gksk-rebate-acl",
    "gksk-rebate-fronted",
    "data-agent",
    "data-center",
]


async def list_repos() -> dict:
    """列出所有可搜索的代码仓库"""
    repos = []
    for name in KNOWN_REPOS:
        path = os.path.join(REBATE_CODE_ROOT, name)
        if os.path.isdir(path):
            repos.append({"name": name, "path": path})
    return {"repos": repos, "count": len(repos), "error": None}


async def search_code(
    keyword: str,
    repo: str = "",
    file_pattern: str = "*.java",
    max_results: int = 20,
) -> dict:
    """
    在代码仓库中搜索关键词

    参数:
        keyword: 搜索关键词 (类名、方法名、错误信息)
        repo: 仓库名，为空则搜索所有仓库
        file_pattern: 文件类型过滤 (默认 *.java)
        max_results: 最大结果数 (默认 20)

    返回:
        {"results": [{"repo":..., "file":..., "line":..., "content":...}], "count": N}
    """
    if repo:
        search_dirs = [os.path.join(REBATE_CODE_ROOT, repo)]
    else:
        search_dirs = [os.path.join(REBATE_CODE_ROOT, r) for r in KNOWN_REPOS]

    results = []
    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue

        repo_name = os.path.basename(search_dir)
        try:
            output = subprocess.run(
                ["grep", "-rn", "--include", file_pattern,
                 "--exclude-dir=target", "--exclude-dir=node_modules",
                 "--exclude-dir=.git", "--exclude-dir=.idea",
                 keyword, search_dir],
                capture_output=True, text=True, timeout=30,
            )
            for line in output.stdout.strip().split("\n")[:max_results]:
                if ":" in line:
                    parts = line.split(":", 2)
                    if len(parts) >= 3:
                        results.append({
                            "repo": repo_name,
                            "file": parts[0].replace(search_dir + "/", ""),
                            "line": parts[1],
                            "content": parts[2].strip()[:200],
                        })
        except subprocess.TimeoutExpired:
            continue

        if len(results) >= max_results:
            break

    return {
        "results": results[:max_results],
        "count": len(results[:max_results]),
        "error": None,
    }


async def read_file(
    repo: str,
    file_path: str,
    max_lines: int = 100,
) -> dict:
    """
    读取代码仓库中的文件内容

    参数:
        repo: 仓库名
        file_path: 相对于仓库根目录的文件路径
        max_lines: 最大行数 (默认 100)

    返回:
        {"content": "...", "total_lines": N, "error": None}
    """
    full_path = os.path.join(REBATE_CODE_ROOT, repo, file_path)
    if not os.path.isfile(full_path):
        return {"content": "", "total_lines": 0, "error": f"文件不存在: {file_path}"}

    try:
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            total = len(lines)
            content = "".join(lines[:max_lines])
            return {
                "content": content,
                "total_lines": total,
                "shown_lines": min(total, max_lines),
                "error": None,
            }
    except Exception as e:
        return {"content": "", "total_lines": 0, "error": str(e)}


async def git_log(
    repo: str,
    since: str = "2026-07-21",
    max_commits: int = 10,
) -> dict:
    """
    查看代码仓库的 Git 提交历史

    参数:
        repo: 仓库名
        since: 起始日期 (YYYY-MM-DD)
        max_commits: 最大提交数 (默认 10)

    返回:
        {"commits": [{hash, author, date, message}], "count": N, "error": None}
    """
    repo_path = os.path.join(REBATE_CODE_ROOT, repo)
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        return {"commits": [], "count": 0, "error": f"不是 Git 仓库: {repo}"}

    try:
        output = subprocess.run(
            ["git", "log", f"--since={since}", f"--max-count={max_commits}",
             "--format=%H|%an|%ai|%s"],
            capture_output=True, text=True, timeout=10,
            cwd=repo_path,
        )
        commits = []
        for line in output.stdout.strip().split("\n"):
            if "|" in line:
                parts = line.split("|", 3)
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0][:8],
                        "author": parts[1],
                        "date": parts[2][:10],
                        "message": parts[3][:100],
                    })
        return {"commits": commits, "count": len(commits), "error": None}
    except Exception as e:
        return {"commits": [], "count": 0, "error": str(e)}
