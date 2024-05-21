import asyncio
import time
import importlib
from datetime import datetime
import json
import inspect
import warnings
from concurrent.futures.thread import ThreadPoolExecutor
from llm_analyst.core.config import Config, ReportType
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.embedding_methods.compressor import ContextCompressor


import logging
logging.basicConfig(filename='llm_analyst.log', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

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

    async def conduct_research(self):
        # Generate Agent
        function_name = inspect.currentframe().f_code.co_name
        logger.debug("TRACE: Entering %s", function_name)
        if not (self.agent and self.role):
            self.agent, self.role = await self._choose_agent()
        self.context = await self.get_context_by_search()
        time.sleep(2)
        logger.debug("TRACE: Exiting %s", function_name)
    
    async def get_context_by_search(self):
        """
           Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """

        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self._get_sub_queries() + [self.query]

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self.process_sub_query(sub_query) for sub_query in sub_queries])

        return context

    async def _choose_agent(self):
        """
        Chooses the agent automatically

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

    async def _get_sub_queries(self):
        """
        Gets the sub queries
        """
        
        if self.report_type == ReportType.DetailedReport.value or self.report_type == ReportType.SubtopicReport.value:
            task = f"{self.parent_query} - {self.query}"
        else:
            task = self.query
    
        deterministic_temp=0
        search_queries_prompt = Prompts().get_prompt("search_queries_prompt",
                                                     max_iterations=self.cfg.max_iterations,
                                                     task=task,
                                                     datetime_now = datetime.now().strftime('%B %d, %Y'))
        messages=[
                {"role": "system", "content": self.role},
                {"role": "user", "content": search_queries_prompt}
                ]

        provider = self.cfg.llm_provider(
                            model=self.cfg.smart_llm_model,
                            temperature=deterministic_temp,
                            max_tokens=self.cfg.smart_token_limit)
        
        response = await provider.get_chat_response(messages=messages)

        sub_queries = json.loads(response)
        return sub_queries


    async def _keep_unique_urls(self, url_set_input):
        """ Parse the URLS and remove any duplicates
        Args: url_set_input (set[str]): The url set to get the new urls from
        Returns: list[str]: The new urls from the given url set
        """

        new_urls = []
        for url in url_set_input:
            if url not in self.visited_urls:
                self.visited_urls.add(url)
                new_urls.append(url)

        return new_urls

    def _scrape_urls(self, urls):
        """
        Scrapes the urls
        Args:
            urls: List of urls

        Returns:
            text: str

        """
        def extract_data_from_link(link):
            if link.endswith(".pdf"):
                scraper_nm = "pdf_scraper"
            elif "arxiv.org" in link:
                scraper_nm = "arxiv_scraper"
            else:
                scraper_nm = "bs_scraper"

            content = ""
            try:
                module_nm="llm_analyst.scrapers.scraper_methods"
                module = importlib.import_module(module_nm)
                scraper = getattr(module, scraper_nm)
                content = scraper(link)

                if len(content) < 100:
                    return {"url": link, "raw_content": None}
                return {"url": link, "raw_content": content}
            except Exception:
                return {"url": link, "raw_content": None}

        content_list = []
        try:
            with ThreadPoolExecutor(max_workers=20) as executor:
                contents = executor.map(extract_data_from_link, urls)
            content_list = [content for content in contents if content["raw_content"] is not None]

        except Exception as e:
            print(f"Error in scrape_urls: {e}")
        return content_list

    async def _scrape_sites_by_query(self, sub_query):
        search_results = self.cfg.internet_search(sub_query, max_results=self.cfg.max_search_results_per_query)
        new_search_urls = await self._keep_unique_urls([url.get("href") for url in search_results])
        scraped_content_results = self._scrape_urls(new_search_urls)
        return scraped_content_results

    async def _get_similar_content_by_query(self, query, pages):
        # Summarize Raw Data
        context_compressor = ContextCompressor(documents=pages, embeddings=self.cfg.embedding_provider)
        # Run Tasks
        return context_compressor.get_context(query, max_results=8)



    async def process_sub_query(self, sub_query: str):
        """Takes in a sub query and scrapes urls based on it and gathers context.

        Args:
            sub_query (str): The sub-query generated from the original query

        Returns:
            str: The context gathered from search
        """

        scraped_sites = await self._scrape_sites_by_query(sub_query)
        content = await self._get_similar_content_by_query(sub_query, scraped_sites)
        return content
    
    ##########################################################################################

    def get_prompt_by_report_type(self):
        report_type_mapping = {
            ReportType.ResearchReport.value: "report_prompt",
            ReportType.ResourceReport.value: "resource_report_prompt",
            ReportType.OutlineReport.value: "outline_report_prompt",
            ReportType.CustomReport.value: "custom_report_prompt", # Not Implemented
            ReportType.SubtopicReport.value: "subtopic_report_prompt"
        }
        prompt_by_type = report_type_mapping.get(self.report_type)
        default_report_type = ReportType.ResearchReport.value
        if not prompt_by_type:
            warnings.warn(f"Invalid report type: {self.report_type}.\n"
                            f"Please use one of the following: {', '.join([enum_value for enum_value in report_type_mapping.keys()])}\n"
                            f"Using default report type: {default_report_type} prompt.",
                            UserWarning)
            prompt_by_type = report_type_mapping.get(default_report_type)
        return prompt_by_type


    async def write_report(self, existing_headers: list = []):
        """
        generates the final report
        Args:
            existing_headers:

        Returns:
            report:

        """
        report_prompt_nm = self.get_prompt_by_report_type()
        report_format = 'APA'
        datetime_now = datetime.now().strftime('%B %d, %Y')
        
        report = ""
        if self.report_type == "custom_report":
            raise LLMAnalystsException("CUSTOM REPORT Not Implemented")
        elif self.report_type == "subtopic_report":
            report_prompt = Prompts().get_prompt(report_prompt_nm,
                                            context=self.context,
                                            current_subtopic=self.query,
                                            main_topic=self.parent_query,
                                            max_subsections=self.cfg.max_subsections,
                                            report_format=report_format,
                                            existing_headers=existing_headers,
                                            datetime_now=datetime_now,
                                            total_words=self.cfg.total_words)
        else:
            report_prompt = Prompts().get_prompt(report_prompt_nm,
                                             context=self.context,
                                             question=self.query,
                                             total_words=self.cfg.total_words,
                                             report_format=report_format,
                                             datetime_now = datetime_now)

        try:
            deterministic_temp=0
            messages=[
                    {"role": "system", "content": self.role},
                    {"role": "user", "content": report_prompt}],
            
            provider = self.cfg.llm_provider(
                            model=self.cfg.smart_llm_model,
                            temperature=deterministic_temp,
                            max_tokens=self.cfg.smart_token_limit)
            
            report = await provider.get_chat_response(messages=messages,stream=True)

        except Exception as e:
            print(f"Error in generate_report: {e}")

        return report

