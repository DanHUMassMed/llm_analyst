import os

from langchain_openai import ChatOpenAI
from llm_analyst.core.exceptions import LLMAnalystsException


class OPENAI_Model:

    def __init__(
        self,
        model,
        temperature,
        max_tokens
    ):
        try:
            api_key = os.environ["OPENAI_API_KEY"]
        except:
            raise LLMAnalystsException("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

        self.llm = ChatOpenAI(
            model = model,
            temperature = temperature,
            max_tokens = max_tokens,
            api_key = api_key
        )

    async def get_chat_response(self, messages, stream=False):
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