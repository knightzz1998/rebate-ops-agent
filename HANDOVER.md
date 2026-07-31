# 返利运维 Agent 平台 — 交接文档

## 项目概述

基于 AgentScope 构建的返利系统运维 Agent，能够自动排查问题：
- 查询 Grafana Loki 日志定位错误
- 查询 PostgreSQL/Doris 数据库核对业务数据
- 搜索代码仓库定位问题模块
- 通过租户映射自动路由到正确的数据库 schema

## 技术栈

| 层 | 技术 |
|---|------|
| Agent 框架 | AgentScope 2.0 (Python 3.11+) |
| 日志查询 | Grafana Loki + rebate-log-query SKILL |
| 数据库查询 | PostgreSQL + Doris + db-readonly-query SKILL |
| 代码搜索 | grep + git (8个返利仓库) |
| 租户管理 | system_code → schema 自动映射 (29租户) |

## 已实现工具 (4个)

### 1. 日志查询 (tools/loki_tool.py)
- 封装 rebate-log-query SKILL 的 query_rebate_loki.py
- 支持 dev/sit/prod 三环境
- 按 app + contains + 时间范围查询
- 自动处理 Grafana session 缓存和刷新
- 引用: `~/.config/opencode/rebate-superpowers/skills/rebate-log-query/`

### 2. 数据库只读查询 (tools/db_tool.py)
- **强制走 db-readonly-query SKILL 的安全校验**
- 仅允许 SELECT/WITH/SHOW/EXPLAIN/DESCRIBE
- 硬性禁止 INSERT/UPDATE/DELETE/DDL/多语句
- system_code → schema 自动映射
- 账号密码从环境变量读取 (REBATE_PG_* / REBATE_DORIS_*)
- 引用: `~/.config/opencode/rebate-superpowers/skills/db-readonly-query/`

### 3. 租户信息查询 (tools/tenant_tool.py)
- 29 个租户编码 ↔ 名称 ↔ PostgreSQL schema 三列映射
- 支持按编码/名称关键词查询
- 数据来源: system_code_schema_map.json + 生产租户对照表

### 4. 代码仓库查询 (tools/code_tool.py)
- 8 个返利仓库 (gksk-rebate-system/account/calculate/aggregate/acl/fronted + data-agent + data-center)
- grep 搜索代码 (自动排除 target/node_modules/.git/)
- 按文件/文件内容阅读
- Git 提交历史查看

## 环境变量配置

```bash
# 日志查询 (Grafana)
# 已配置在 rebate-log-query SKILL 的 references/log-env-config.json

# 数据库查询 (模板: config/db_env.template.sh)
# 复制模板填入真实密码，不要提交到 git
cp config/db_env.template.sh config/db_env.sh
# 编辑 db_env.sh 填入各环境真实密码
source config/db_env.sh

# AgentScope 模型
export DEEPSEEK_API_KEY="你的key"
```

## 安全规则

1. 数据库密码、API Key 不在代码中硬编码
2. 配置文件模板可提交 (`.template.*`)，真实配置不提交
3. 所有数据库查询必须经过 SKILL 安全校验
4. 仅允许 SELECT，禁止任何写操作

## 项目结构

```
rebate-ops-agent/
├── agents/           # Agent 定义 (leader/diagnoser 待完善)
├── skills/           # SKILL 文档 (log-query/db-readonly/code-repo/tenant-mapping)
├── tools/            # 工具实现 ⭐ 核心
│   ├── loki_tool.py   # 日志查询 (✅ 已实现)
│   ├── db_tool.py     # 数据库查询 (✅ 已实现)
│   ├── tenant_tool.py # 租户信息 (✅ 已实现)
│   └── code_tool.py   # 代码仓库 (✅ 已实现)
├── config/           # 配置文件
│   ├── agents.yaml
│   └── db_env.template.sh
├── main.py           # 服务入口 (待完善: AgentScope Agent 创建)
└── requirements.txt
```

## 待办事项

- [ ] main.py: 完成 AgentScope Agent 的创建和工具集成
- [ ] 租户名称从数据库真实关联 (当前为已知映射)
- [ ] 前端 Web UI
- [ ] Docker 部署
- [ ] Agent 评测框架
- [ ] Agent Team (Leader + Worker) 实际编排

## 关联知识库

本项目的理论知识在独立仓库:
- `ai-agent-dev`: 知识笔记 + 项目文档 (Obsidian)
- `ai-agent-code`: 所有 Python/Java 代码示例
- GitHub: https://github.com/knightzz1998/
