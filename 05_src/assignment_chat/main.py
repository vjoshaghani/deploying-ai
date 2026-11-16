import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import tracing_context

from assignment_chat.agent_tools import build_tools
from assignment_chat.prompts import return_instructions


SOURCE_DIR = Path(__file__).resolve().parent.parent


def get_graph():
    """Build the model-and-tools conversation workflow."""
    load_dotenv(SOURCE_DIR / ".env")
    load_dotenv(SOURCE_DIR / ".secrets")

    gateway_key = os.getenv("API_GATEWAY_KEY")
    if not gateway_key:
        raise ValueError("The course API_GATEWAY_KEY is missing.")

    model = ChatOpenAI(
        model=os.getenv("MODEL", "gpt-4o-mini"),
        api_key="any value",
        base_url=(
            "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com"
            "/prod/openai/v1"
        ),
        default_headers={"x-api-key": gateway_key},
        temperature=0,
        timeout=30,
        max_retries=1,
    )

    tools = build_tools()
    model_with_tools = model.bind_tools(tools)

    def call_model(state: MessagesState):
        today = datetime.now(
            ZoneInfo("America/Toronto")
        ).date().isoformat()

        instructions = (
            return_instructions()
            + f"\nToday's date in Ottawa is {today}."
        )

        response = model_with_tools.invoke(
            [SystemMessage(content=instructions)]
            + state["messages"]
        )

        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    builder.add_node("call_model", call_model)
    builder.add_node(
        "tools",
        ToolNode(
            tools,
            handle_tool_errors=(
                "The tool could not complete this request. "
                "Check the inputs or explain that it is unavailable. "
                "Do not invent a result."
            ),
        ),
    )

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")

    return builder.compile()


def run_conversation(graph, messages):
    """Run a conversation turn without optional LangSmith logging."""
    with tracing_context(enabled=False):
        return graph.invoke(
            {"messages": messages},
            config={"recursion_limit": 12},
        )