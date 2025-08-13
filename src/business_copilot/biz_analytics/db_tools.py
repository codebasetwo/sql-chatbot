import asyncio
import asyncpg
from langchain_core.tools import tool
from langchain_openai import OpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from business_copilot.biz_analytics.utils import (
    throttle,
    get_example, 
    create_table_schema)
from business_copilot.biz_analytics.pgres_utils import get_connection_pool
from business_copilot.biz_analytics.prompts import (
    DOUBLE_CHECK_PROMPT,
    ERROR_PROMPT,
    )


LLM = OpenAI(model="gpt-4o-mini", temperature=0.0)


@tool 
async def list_tables()-> list[str]:
    """Get all the list of tables in the database."""
    pool = await get_connection_pool()
    # Get columns
    async with pool.acquire() as conn:
        #conn = await get_connection()
        rows = await conn.fetch("""
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema';
        """)
        return [row['tablename'] for row in rows]


@tool
async def get_relevant_schema_example(table_names: list[str]) -> str:
    """Get schema and examples for requested list of table or tables relevant to the question.
    Args:
        table_names: the name of the table to get data from.
    """
    
    schemas = [throttle(create_table_schema(names.lower()))
                for names in table_names]
    
    examples = [throttle(get_example(names.lower())) 
                for names in table_names]
    
    schemas = await asyncio.gather(*schemas)
    examples = await asyncio.gather(*examples)
    rel_schema = ""
    for schema, eg in zip(schemas, examples):   
        rel_schema += schema + "\n\n" + eg + "\n\n"
        
    return rel_schema


@tool
async def double_check_query(query: str):
    """Use this tool to double check if your query is correct before executing it.
        Always use this tool before executing a query with execute_query!

    Args:
        query: a query that contains the generated SQL query
    """

    prompt = PromptTemplate(
        input_variables=["query"], template=DOUBLE_CHECK_PROMPT
    )
    chain = prompt | LLM | StrOutputParser()

    return await chain.ainvoke({"query": query})


@tool
async def resolve_error(query: str, error: str):
    """Use this tool resolve the error that a query generated.
     only use this tool when there is an error.

    Args:
        query: a query that contains the generated SQL query
    """

    prompt = PromptTemplate(
        input_variables=["query", "error"], template=ERROR_PROMPT
    )
    chain = prompt | LLM | StrOutputParser()

    return await chain.ainvoke({"query": query, "error": error})


@tool
async def execute_query(query: str) -> str | asyncpg.Record:
    """Executes the given detailed input SQL query.
    Args:
        query: the sql query which to get information from the database.
    """
    # global conn
    # if conn is None:
    #     conn = await get_connection()
    pool = await get_connection_pool()
    async with pool.acquire() as conn:
        try:
            values = await conn.fetch(
                query,
            )
            return values
        except Exception as e:
            return f"Error: {e}"


@tool
async def clean_up()-> None:
    """Close the connection to the databse."""
    pool = await get_connection_pool()
    async with pool.acquire() as conn:
    #if conn is not None:
        await conn.close()


if __name__ == "__main__":
    pass
c = "https://blog.patterns.app/blog/2023/01/18/crunchbot-sql-analyst-gpt"