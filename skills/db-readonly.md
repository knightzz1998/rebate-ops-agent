# 数据库只读查询 Skill
# 用途: 安全查询 PostgreSQL/Doris 业务数据
# 使用方式: Agent 加载此 Skill 后自动获得数据库只读查询能力

## 能力描述
你可以查询返利系统的业务数据库。支持 PostgreSQL 和 Doris，按 system_code 自动切换 schema。

## 查询参数
- system_code: 租户编码 (自动映射 schema)
- sql: SQL 语句 (仅允许 SELECT，禁止 INSERT/UPDATE/DELETE/DDL)
- format: 输出格式 table/csv/markdown

## 使用示例
1. 核对返利单数据:
   查询 system_code=1000, sql="SELECT * FROM rebate_order WHERE order_id = 'xxx'"

2. 检查数据一致性:
   查询 sql="SELECT COUNT(*), status FROM rebate_order GROUP BY status"

3. 查看最近创建的记录:
   查询 sql="SELECT * FROM rebate_order ORDER BY create_time DESC LIMIT 20"

## 注意事项
- 仅允许 SELECT 查询
- 禁止 JOIN 超过 3 张表 (避免慢查询)
- 每��查询最多返回 500 行
- 禁止查询包含密码、密钥等敏感字段
- 生产环境查询需记录审计日志
