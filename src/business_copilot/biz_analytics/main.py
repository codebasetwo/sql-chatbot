from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from business_copilot.biz_analytics.db_tools import (list_tables, 
                                                     get_relevant_schema_example, 
                                                     resolve_error, 
                                                     execute_query,
                                                     double_check_query,
                                                     clean_up)
from business_copilot.biz_analytics.prompts import POSTGRES_SYSTEM_MESSAGE
from business_copilot.biz_analytics.utils import visualize_graph

tools = [
    list_tables, get_relevant_schema_example,
    resolve_error, execute_query, 
    double_check_query, clean_up
]


# Create graph
model = "gpt-4o-mini"
llm = init_chat_model(f"openai:{model}")
agent_executor = create_react_agent(llm , tools=tools, prompt=POSTGRES_SYSTEM_MESSAGE)


if __name__ == "__main__":
    file_name = "mermaid_graph.png"
    visualize_graph(agent_executor, file_name, xray=True)