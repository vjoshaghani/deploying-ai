import gradio as gr
from langchain_core.messages import HumanMessage

from assignment_chat.main import get_graph, run_conversation
from assignment_chat.guardrails import (
    REFUSAL,
    contains_restricted_topic,
    is_blocked_input,
)


graph = get_graph()


def extract_text(content):
    """Read plain text or text blocks from a chat message."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
        )

    return ""


def ottawa_chat(message, history, conversation_state):
    """Use full session history, including previous tool calls and results."""
    # An empty visible chat starts a fresh conversation.
    if not history:
        conversation_state = []

    if is_blocked_input(message):
        return REFUSAL, conversation_state

    # Make a new list so a failed request doesn't alter saved state.
    messages = list(conversation_state or [])
    messages.append(HumanMessage(content=message))

    try:
        result = run_conversation(graph, messages)
    except Exception:
        raise gr.Error(
            "The request could not be completed. "
            "Please check your connection and try again."
        ) from None

    answer = extract_text(result["messages"][-1].content)

    if not answer:
        return (
            "I couldn't produce an answer. Please try rephrasing.",
            conversation_state,
        )

    if contains_restricted_topic(answer):
        return REFUSAL, conversation_state

    # Display only the answer, but retain ALL messages for the next turn.
    return answer, result["messages"]


with gr.Blocks() as demo:
    conversation_state = gr.State([])

    chat = gr.ChatInterface(
        fn=ottawa_chat,
        additional_inputs=[conversation_state],
        additional_outputs=[conversation_state],
        title="Ottawa Day Trip Planner",
        description=(
            "Find attractions, check the weather, and estimate your day's "
            "time and cost. Admission prices are demo values."
        ),
        examples=[
            ["Recommend one indoor attraction for someone interested in aircraft."],
            ["What is the Ottawa weather forecast for tomorrow?"],
            ["Help me plan a day for two adults interested in art and history."],
        ],
        cache_examples=False,
        save_history=False,
    )

    # Clear the internal conversation when the visible chat is cleared.
    chat.chatbot.clear(
        fn=lambda: [],
        outputs=[conversation_state],
        queue=False,
    )


if __name__ == "__main__":
    demo.launch(
        server_name="127.0.0.1",
        share=False,
        inbrowser=True,
    )