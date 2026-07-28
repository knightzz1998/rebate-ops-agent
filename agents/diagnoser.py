"""
返利运维 Agent - 诊断员

负责:
  1. 查询日志定位错误
  2. 查询数据库核对数据
  3. 搜索代码定位问题模块
  4. 给出根因分析
"""

from agentscope.agent import Agent


def create_diagnoser_agent(model, toolkit, system_prompt: str) -> Agent:
    """创建诊断 Agent"""
    return Agent(
        name="诊断员",
        system_prompt=system_prompt,
        model=model,
        toolkit=toolkit,
    )
