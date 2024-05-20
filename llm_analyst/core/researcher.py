import asyncio
import time
import json
from llm_analyst.core.config import Config, ReportType
from llm_analyst.core.prompts import Prompts
from llm_analyst.embedding_methods.compressor import ContextCompressor



class LLMAnalyst:
    def __init__(
        self,
        query: str,
        report_type:  str = ReportType.ResearchReport,
        agent = None,
        role  = None,
        parent_query: str = "",
        visited_urls: set = set()
    ):
        self.query = query
        self.report_type = report_type
        self.agent = agent
        self.role = role
        self.cfg = Config()
        self.context = []
        # Used for detailed reports
        self.parent_query = parent_query
        self.visited_urls = visited_urls

    async def _choose_agent(self):
        """
        Chooses the agent automatically
        Args:
            parent_query: In some cases the research is conducted on a subtopic from the main query.
            The parent query allows the agent to know the main context for better reasoning.
            query: original query
            cfg: Config

        Returns:
            agent: Agent name
            agent_role_prompt: Agent role prompt
        """
        try:
            deterministic_temp=0
            auto_agent_instructions = Prompts().get_prompt("auto_agent_instructions")
            query = f"{self.parent_query} - {self.query}" if self.parent_query else f"{self.query}"
            messages=[
                    {"role": "system", "content": auto_agent_instructions},
                    {"role": "user", "content": f"task: {query}"}]
            
            provider = self.cfg.llm_provider(
                            model=self.cfg.smart_llm_model,
                            temperature=deterministic_temp,
                            max_tokens=self.cfg.smart_token_limit)

            response = await provider.get_chat_response(messages=messages)
            agent_dict = json.loads(response)
            return agent_dict["server"], agent_dict["agent_role_prompt"]
        except Exception as e:
            return "Default Agent", "You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text."

    async def get_context_by_search(self):
        """
           Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await get_sub_queries(query, self.role, self.cfg, self.parent_query, self.report_type)

        # If this is not part of a sub researcher, add original query to research for better results
        if self.report_type != "subtopic_report":
            sub_queries.append(query)

        if self.verbose:
            await stream_output("logs",
                                f"🧠 I will conduct my research based on the following queries: {sub_queries}...",
                                self.websocket)

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self.process_sub_query(sub_query) for sub_query in sub_queries])
        return context
