"""
This module provides an interface for interacting with the Groq models using 
the `ChatGroq` class from the `langchain_groq` package.

https://groq.com/
"""
import os

from langchain_groq import ChatGroq
from llm_analyst.core.exceptions import LLMAnalystsException


class GROQ_Model:

    def __init__(self, model, temperature, max_tokens):
        try:
            api_key = os.environ["GROQ_API_KEY"]
        except:
            raise LLMAnalystsException(
                "Groq API key not found. Please set the GROQ_API_KEY environment variable."
            )

        self.llm = ChatGroq(
            model=model, temperature=temperature, max_tokens=max_tokens, api_key=api_key
        )

    async def get_chat_response(self, llm_system_prompt, llm_user_prompt, stream=False):
        messages = [
            {"role": "system", "content": llm_system_prompt},
            {"role": "user", "content": f"task: {llm_user_prompt}"},
        ]
        response = ""
        if not stream:
            output = await self.llm.ainvoke(messages)
            response = output.content
        else:
            response = await self._get_stream_response(messages)

        return response

    async def _get_stream_response(self, messages):
        paragraph = ""
        response = ""

        # Streaming the response using the chain astream method from langchain
        async for chunk in self.llm.astream(messages):
            content = chunk.content
            if content is not None:
                response += content
                paragraph += content
                if "\n" in paragraph:
                    print(f"{paragraph}")
                    paragraph = ""

        return response
