# 日志查询 Skill
# 用途: 查询 Grafana Loki 日志，定位错误和异常
# 使用方式: Agent 加载此 Skill 后自动获得日志查询能力

## 能力描述
你可以查询返利系统在 DEV/SIT/PROD 环境的运行日志。支持按时间范围、应用名、关键词筛选。

## 查询参数
- env: dev / sit / prod (切换目标环境)
- app: 应用名 (如 gksk-rebate-system)
- contains: 日志关键词
- time_from: 开始时间 (默认 now-5m)
- time_to: 结束时间 (默认 now)
- limit: 最大返回条数 (默认 100)

## 使用示例
1. 排查审批异常:
   查询 env=prod, app=gksk-rebate-system, contains="审批失败", time_from=now-1h

2. 排查 MQ 消费:
   查询 env=sit, contains="消费异常", limit=50

3. 查看服务启动日志:
   查询 env=dev, contains="started", time_from=now-10m

## 注意事项
- PROD 环境只读查询，禁止修改
- 每次查询最多返回 200 条
- 注意日志中的敏感信息脱敏
