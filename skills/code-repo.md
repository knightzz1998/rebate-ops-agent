# 代码仓库查询 Skill
# 用途: 搜索代码仓库，定位问题模块
# 使用方式: Agent 加载此 Skill 后自动获得代码搜索能力

## 能力描述
你可以搜索返利系统的代码仓库，支持按关键词搜索、查看文件内容、查看 Git 历史。

## 查询参数
- repo: 代码仓库路径 (默认搜索所有返利仓库)
- keyword: 搜索关键词 (类名、方法名、错误信息)
- file_pattern: 文件类型过滤 (如 "*.java", "*.py")
- git_branch: Git 分支 (默认当前分支)

## 使用示例
1. 定位错误来源:
   搜索 keyword="NullPointerException", repo=rebate-system

2. 查看接口实现:
   搜索 keyword="createRebateOrder", file_pattern="*.java"

3. 查看最近改动:
   查看 git_log repo=rebate-system, since="2026-07-20"

## 注意事项
- 只读操作，不会修改代码
- 跨仓库搜索时注意性能
- 涉及安全模块的代码搜索结果需脱敏
