import argparse
import asyncio
from typing import Optional

from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver

from business_copilot.biz_analytics.db_tools import (list_tables, 
                                                     get_relevant_schema_example, 
                                                     resolve_error, 
                                                     execute_query,
                                                     double_check_query,
                                                     clean_up)
from business_copilot.biz_analytics.prompts import POSTGRES_SYSTEM_MESSAGE
from business_copilot.biz_analytics.utils import visualize_graph 
from business_copilot.biz_analytics.memory import SumNode
from business_copilot.biz_analytics.schemas import State

tools = [
    list_tables, get_relevant_schema_example,
    resolve_error, execute_query, 
    double_check_query, clean_up
]


async def create_agent(model: str, temperature: float, thread_id: Optional[str] = None):
    checkpointer = InMemorySaver() if thread_id else None
    config = ({
    "configurable": {
        "thread_id": thread_id
            }
        } if thread_id else None )

    llm = init_chat_model(f"openai:{model}", temperature=temperature)
    agent_executor = create_react_agent(
        llm , 
        tools=tools, 
        prompt=POSTGRES_SYSTEM_MESSAGE,
        pre_model_hook=SumNode,
        state_schema=State,
        checkpointer=checkpointer, # Use a database for production.
    )
    while True:
            try:
                user_input = input("Human: ")
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Goodbye!")
                    break
                async for steps in agent_executor.astream({"messages":[HumanMessage(content=user_input.lower())]}, 
                                     config= config, 
                                     stream_mode="values"
                                     ):
                        print(steps["messages"][-1].pretty_print())

            except Exception as e:
                print(f"\nError: {str(e)}")
                break
    
    

def main():
    parser = argparse.ArgumentParser(
        description="Ask a question to the agent and optionally pass a thread ID."
    )
    parser.add_argument(
        "model",
        type=str,
        help="the model to use."
    )
    parser.add_argument(
        "--temp",
        type=float,
        default=0.7,
        help="the amount to vary model response"
    )
    parser.add_argument(
        "--thread_id",
        type=str,
        default=None,
        help="Optional thread ID for context"
    )
        
    args = parser.parse_args()
    asyncio.run(create_agent(
        model=args.model,
        temperature=args.temp,
        thread_id = args.thread_id)
        )    
    

if __name__ == "__main__":
    # file_name = "mermaid_graph.png"
    # visualize_graph(agent_executor, file_name, xray=True)
    main()