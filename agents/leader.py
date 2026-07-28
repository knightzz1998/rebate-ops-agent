"""
返利运维 Agent - 协调者 (Leader)

负责:
  1. 理解运维人员的任务
  2. 拆解为子任务
  3. 分发到专业 Worker Agent
  4. 汇总结果
"""

from agentscope.agent import Agent


def create_leader_agent(model, toolkit, system_prompt: str) -> Agent:
    """创建运维 Leader Agent"""
    return Agent(
        name="运维协调员",
        system_prompt=system_prompt,
        model=model,
        toolkit=toolkit,
    )
