# 返利运维 Agent 平台

## 架构

```
┌─────────────────────────────────────────────────────┐
│                   Web UI (对话 + 面板)                  │
└──────────────────────────┬──────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│              AgentScope Agent Service                │
│  • 多租户(按业务线)  • 多会话  • 权限控制               │
├─────────────────────────────────────────────────────┤
│              Agent Team (Leader + Worker)            │
│                                                      │
│  Leader: 任务规划 + 协调                               │
│    ├── 巡检 Agent: 定时扫描日志/告警                    │
│    ├── 诊断 Agent: 根因分析 + 知识库检索                │
│    ├── 修复 Agent: 执行安全修复(需确认)                 │
│    └── 报告 Agent: 生成运维日报/周报                    │
├─────────────────────────────────────────────────────┤
│                    工具层 (MCP/Skill)                 │
│  • 日志查询 (Loki/Grafana)                            │
│  • 数据库只读查询 (PostgreSQL/Doris)                   │
│  • 代码仓库查询 (Git/GitHub)                           │
│  • 监控指标 (Prometheus)                               │
│  • 审批工作流  • 通知(钉钉/飞书)                        │
└─────────────────────────────────────────────────────┘
```

## 项目结构

```
rebate-ops-agent/
├── agents/           # Agent 定义
│   ├── leader.py     # 协调者
│   ├── inspector.py  # 巡检 Agent
│   ├── diagnoser.py  # 诊断 Agent
│   ├── fixer.py      # 修复 Agent
│   └── reporter.py   # 报告 Agent
├── skills/           # Skill 定义 (Markdown 指令集)
│   ├── log-query.md         # 日志查询
│   ├── db-readonly.md       # 数据库只读查询
│   ├── code-repo.md         # 代码仓库操作
│   └── monitor.md           # 监控指标查询
├── tools/            # 工具实现
│   ├── loki_tool.py         # Grafana Loki 日志查询
│   ├── db_tool.py           # PostgreSQL/Doris 只读查询
│   ├── git_tool.py          # 代码仓库操作
│   └── alert_tool.py        # 钉钉/飞书通知
├── config/           # 配置文件
│   ├── env.yaml             # 环境配置 (DEV/SIT/PROD)
│   ├── agents.yaml          # Agent 配置
│   └── tools.yaml           # 工具/MCP 配置
├── main.py           # 服务入口
├── requirements.txt
└── README.md
```

## 技��栈

- Agent 框架: AgentScope 2.0
- 后端: Python 3.11+ / FastAPI
- 存储: Redis (会话 + 状态) + PostgreSQL (业务数据)
- 工具协议: MCP (连接外部系统)
- 前端: React (后续)

## 开始

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务
python main.py
```
