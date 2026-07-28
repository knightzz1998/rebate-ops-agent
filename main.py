"""
返利运维 Agent — 服务入口
"""

import os
from agentscope.agent import Agent
from agentscope.tool import Toolkit, Bash, Grep, Glob, Read
from agentscope.model import OpenAIChatModel
from agentscope.credential import OpenAICredential


def build_leader():
    """构建运维 Leader Agent (首期单 Agent 模式，后续扩展为 Team)"""
    model = OpenAIChatModel(
        credential=OpenAICredential(api_key=os.getenv("DEEPSEEK_API_KEY")),
        model="deepseek-v4-flash",
        api_base="https://api.deepseek.com/v1",
    )

    toolkit = Toolkit(tools=[Bash(), Grep(), Glob(), Read()])

    return Agent(
        name="返利运维助手",
        system_prompt="""你是返利系统的运维助手。

你可以:
1. 查询日志 (Loki) — 排查审批异常、MQ消费、服务错误
2. 查询数据库 (只读) — 核对返利单、检查数据一致性
3. 搜索代码 — 定位问题模块、查看接口实现
4. 执行诊断 — 根据错误信息定位根因

注意:
- 生产环境操作需要人工确认
- 禁止执行写操作 (INSERT/UPDATE/DELETE)
- 查询结果较多时主动建议缩小范围""",
        model=model,
        toolkit=toolkit,
    )


if __name__ == "__main__":
    print("返利运维 Agent 平台")
    print("AgentScope 版本初始化中...")
