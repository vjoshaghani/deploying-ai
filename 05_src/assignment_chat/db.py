import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction


PROJECT_DIR = Path(__file__).resolve().parent
SOURCE_DIR = PROJECT_DIR.parent


class CourseEmbeddingFunction(OpenAIEmbeddingFunction):
    """Use gateway credentials without saving them in Chroma's config."""

    def get_config(self):
        config = super().get_config()
        config["default_headers"] = {}
        return config


def open_collection(create=False):
    """Open saved attractions; optionally create during preparation."""
    load_dotenv(SOURCE_DIR / ".env")
    load_dotenv(SOURCE_DIR / ".secrets")

    gateway_key = os.getenv("API_GATEWAY_KEY")
    if not gateway_key:
        raise ValueError("The course API_GATEWAY_KEY is missing.")

    embedding_function = CourseEmbeddingFunction(
        model_name="text-embedding-3-small",
        api_key="any value",
        api_base=(
            "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com"
            "/prod/openai/v1"
        ),
        default_headers={"x-api-key": gateway_key},
    )

    client = chromadb.PersistentClient(
        path=str(PROJECT_DIR / "chroma_db")
    )

    if create:
        return client.get_or_create_collection(
            name="ottawa_attractions",
            embedding_function=embedding_function,
        )

    return client.get_collection(
        name="ottawa_attractions",
        embedding_function=embedding_function,
    )