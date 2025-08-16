from langchain.chat_models import init_chat_model
from langchain_core.messages.utils import count_tokens_approximately
from langmem.short_term import SummarizationNode


summarization_llm = init_chat_model("openai:gpt-4o",)

SumNode = SummarizationNode( 
    token_counter=count_tokens_approximately,
    model=summarization_llm,
    max_tokens=4096, 
    max_summary_tokens=2048,
    output_messages_key="summarized_llm_messages",
)