from .models.llm import LLM
from .prompts import get_chat_prompt, get_standalone_query_generation_prompt
from .retriever import Retriever
from typing import Optional
import base64


class Pipeline:
    def __init__(self):
        self.llm = LLM()
        self.retriever = Retriever()
        self.history = []

    def _generate_standalone_query(self, query: str) -> str:
        """Generate a standalone query if history exists, else return original query."""
        if not self.history:
            return query

        prompt = get_standalone_query_generation_prompt(query, history=self.history)
        standalone_query = self.llm.generate_response(prompt)
        print(f"Standalone Query: {standalone_query}")
        return standalone_query

    def _retrieve_context(self, standalone_query: str) -> str:
        """Retrieve context using the retriever."""
        context = self.retriever.retrieve(standalone_query)
        print(f"Retrieved context: {context}")
        return context

    def _generate_response(self, query: str, context: str = None, image_data: Optional[bytes] = None) -> str:
        """
        Generate assistant response based on query, history, and retrieved context.
        Now supports optional image input for multimodal processing.
        """
        if image_data:
            # Convert image bytes to base64 for LLM processing
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # If your LLM supports multimodal input, pass both text and image
            # This depends on your LLM implementation
            response = self.llm.generate_response(
                query,
                image_base64=image_base64
            )
        else:
            # Text-only processing
            response = self.llm.generate_response(query)

        return response

    def _update_history(self, query: str, response: str) -> None:
        """Update conversation history with user query and assistant response."""
        self.history.extend([
            ("user", query),
            ("assistant", response),
        ])

    def run(self, query: str, image_data: Optional[bytes] = None) -> str:
        """
        Run the full RAG pipeline for a given user query.
        Now supports optional image input.

        Args:
            query: The user's text query
            image_data: Optional image bytes for multimodal processing

        Returns:
            The assistant's response
        """
        # standalone_query = self._generate_standalone_query(query)
        # context = self._retrieve_context(standalone_query)

        response = self._generate_response(query, image_data=image_data)

        # self._update_history(query, response)
        return response

