"""
返利运维 Agent — 服务入口

用法:
  python main.py
"""
import os, asyncio
from agentscope.agent import Agent
from agentscope.tool import Toolkit, FunctionTool
from agentscope.model import OpenAIChatModel
from agentscope.credential import OpenAICredential
from agentscope.message import UserMsg
from agentscope.event import EventType

from tools.loki_tool import query_logs


async def main():
    model = OpenAIChatModel(
        credential=OpenAICredential(api_key=os.getenv("DEEPSEEK_API_KEY")),
        model="deepseek-v4-flash",
        api_base="https://api.deepseek.com/v1",
    )

    agent = Agent(
        name="返利运维助手",
        system_prompt="""你是返利系统的运维助手。

你可以:
1. **查询日志** — 使用 query_logs 查询 Grafana Loki 日志
   - 排查审批异常、MQ消费、服务错误
   - 参数: env(环境) / app(应用名) / contains(关键词) / time_from / time_to
2. **分析日志** — 结合业务知识解读日志内容
3. **排查问题** — 从日志中定位根因

常用应用名:
  - gksk-rebate-system: 返利核心系统
  - gksk-rebate-account: 返利审批核销系统

注意:
- 生产环境查询需确认
- 优先用 writeOffId / approveDocNo / billNo 等业务主键查询""",
        model=model,
        toolkit=Toolkit(tools=[FunctionTool(query_logs)]),
    )

    print("=" * 60)
    print("返利运维 Agent 平台")
    print("=" * 60)

    while True:
        user_input = input("\n> ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            print("再见~")
            break

        print("Agent: ", end="", flush=True)
        async for event in agent.reply_stream(
            UserMsg(name="运维人员", content=user_input)
        ):
            if hasattr(event, "delta"):
                print(event.delta, end="", flush=True)
        print()


if __name__ == "__main__":
    asyncio.run(main())
