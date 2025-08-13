import os
import asyncio
from dataclasses import dataclass
from typing import Awaitable, TypeVar, Union
import pandas as pd
from langgraph.graph.state import CompiledStateGraph
from business_copilot.biz_analytics.pgres_utils import get_connection_pool


THROTTLE_LIMIT = 5
T = TypeVar("T")

async def throttle(coro: Awaitable[T]) -> Union[T, str]:
    async with asyncio.Semaphore(THROTTLE_LIMIT):
        try:
            return await coro
        except Exception as e:
            return f"Error: {str(e)}"
        

async def create_table_schema(table_name: str) -> str:
    """Create a formatted schema for a given table name in a database.\
    
    Args:
        table_name: the name of the table to get data from.
        
    Return:
        str: returns string eith the schema of the table.
    """
    
    # global conn
    pool = await get_connection_pool()
    # Get columns
    async with pool.acquire() as conn:
        columns = await conn.fetch(f"""
            SELECT column_name, data_type, is_nullable, character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position;
        """)

        # Get primary keys
        pk_rows = await conn.fetch(f"""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = '{table_name}'::regclass AND i.indisprimary;
        """)
        primary_keys = [row['attname'] for row in pk_rows]

        # Get foreign keys
        fk_rows = await conn.fetch(f"""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table,
                ccu.column_name AS foreign_column
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = '{table_name}';
        """)

    # Build column definitions
    col_defs = []
    for col in columns:
        name = f'"{col["column_name"]}"'
        dtype = col["data_type"].upper()
        if dtype == "CHARACTER VARYING":
            dtype = f'NVARCHAR({col["character_maximum_length"]})'
        elif dtype == "CHARACTER":
            dtype = f'NCHAR({col["character_maximum_length"]})'
        elif dtype == "TEXT":
            dtype = "TEXT"
        elif dtype == "INTEGER":
            dtype = "INTEGER"
        # Add more type mappings if needed

        nullable = "NOT NULL" if col["is_nullable"] == "NO" else ""
        col_defs.append(f"{name} {dtype} {nullable}".strip())

    # Add primary key
    if primary_keys:
        pk = ', '.join(f'"{key}"' for key in primary_keys)
        col_defs.append(f"PRIMARY KEY ({pk})")

    # Add foreign keys
    for fk in fk_rows:
        col_defs.append(
            f'FOREIGN KEY("{fk["column_name"]}") REFERENCES "{fk["foreign_table"]}" ("{fk["foreign_column"]}")'
        )

    # Final SQL
    sql = f'CREATE TABLE "{table_name}" (\n\t' + ',\n\t'.join(col_defs) + '\n);'     
    return sql


async def get_example(table_name: str) -> str:
    """Get 3 examples from the requested table to be passed as context to the model

    Args:
        table_name: the name of the table to get data from.
    """
    # Execute a query to get exmaple to be passed
    pool = await get_connection_pool()
    # Get columns
    async with pool.acquire() as conn:
        values = await conn.fetch(
            f"SELECT * FROM {table_name} LIMIT 3;",

        )
    examples = []
    for item in values:
        examples.append(list(item.items()))

    records = [dict(row) for row in examples]
    
    table = pd.DataFrame(records).to_string()

    return ("/*\n" + f"3 rows from '{table_name}' table:\n" + table + "\n"+
            "*/"
    )


@dataclass
class NodeStyles:
    default: str = (
        "fill:#45C4B0, fill-opacity:0.3, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:bold, line-height:1.2"
    )
    first: str = (
        "fill:#45C4B0, fill-opacity:0.1, color:#23260F, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2"
    )
    last: str = (
        "fill:#45C4B0, fill-opacity:1, color:#000000, stroke:#45C4B0, stroke-width:1px, font-weight:normal, font-style:italic, stroke-dasharray:2,2"
    )

# Define a function to visualize the graph
def visualize_graph(graph: CompiledStateGraph, filename: str, xray=False):
    """
    Displays a visualization of the CompiledStateGraph object.

    This function converts the given graph object,
    if it is an instance of CompiledStateGraph, into a Mermaid-formatted PNG image and displays it.

    Args:
        graph: The graph object to be visualized. Must be an instance of CompiledStateGraph.

    Returns:
        None

    Raises:
        Exception: Raised if an error occurs during the graph visualization process.
    """
    try:
        # Visualize the graph
        if isinstance(graph, CompiledStateGraph):
            img_bytes = graph.get_graph(xray=xray).draw_mermaid_png(
                        background_color="white",
                        node_colors=NodeStyles(),
                    )
            output_path = os.path.join(os.getcwd(), filename)
            with open(output_path, "wb") as f:
                f.write(img_bytes)
    except Exception as e:
        print(f"[ERROR] Visualize Graph Error: {e}")