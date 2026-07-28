# 代码仓库查询 Skill

## 能力
- 按关键词搜索 Java/Python 代码
- 查看文件内容
- 查看 Git 提交历史
- 列出所有可搜索仓库

## 仓库列表 (8个)
- gksk-rebate-system: 返利核心系统
- gksk-rebate-account: 审批核销系统
- gksk-rebate-calculate: 计算引擎
- gksk-rebate-aggregate: 数据聚合
- gksk-rebate-acl: 权限控制
- gksk-rebate-fronted: 前端
- data-agent: 数据 Agent
- data-center: 数据中心

## 使用示例
1. 定位审批状态枚举:
   搜索 keyword="ApproveDocStatus", repo="gksk-rebate-account", pattern="*.java"

2. 查看接口实现:
   搜索 keyword="createRebateOrder", pattern="*.java"
   然后 read_file 查看完整文件

3. 排查最近改动:
   git_log repo="gksk-rebate-system", since="2026-07-20"

## 注意事项
- 只读操作，不会修改代码
- 自动排除 target/ node_modules/ .git/ .idea/
- 跨仓库搜索时注意性能，建议指定具体仓库
