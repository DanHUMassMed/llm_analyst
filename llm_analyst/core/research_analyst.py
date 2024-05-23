import asyncio
import time
import importlib
from datetime import datetime
import json
import re
import warnings
from concurrent.futures.thread import ThreadPoolExecutor
from llm_analyst.core.config import Config, ReportType
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.embedding_methods.compressor import ContextCompressor
from llm_analyst.utils.app_logging import trace_log, logging
from llm_analyst.core.research_state import ResearchState
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List
from pydantic import BaseModel, Field

class LLMAnalyst(ResearchState):
    def __init__(
        self,
        active_research_topic: str,
        report_type = ReportType.ResearchReport.value,
        agent_type = None,
        agents_role_prompt  = None,
        config = Config(),
        main_research_topic: str = "",
        visited_urls: set = set()
    ):
        super().__init__(active_research_topic=active_research_topic, 
                         report_type=report_type, 
                         agent_type=agent_type, 
                         agents_role_prompt=agents_role_prompt, 
                         main_research_topic=main_research_topic, 
                         visited_urls=visited_urls)
        self.cfg = config
        self.llm_provider = self.cfg.llm_provider(
            model = self.cfg.llm_model,
            temperature = self.cfg.llm_temperature,
            max_tokens = self.cfg.llm_token_limit)

    async def conduct_research(self):
        # Generate Agent
        if not (self.agent_type):
            await self.choose_agent()
        self.research_findings = await self._get_context_by_search()
        return self.get_research_state()
        
        
    
    def get_research_state(self):
        research_state = ResearchState(active_research_topic=self.active_research_topic, 
                         report_type=self.report_type, 
                         agent_type=self.agent_type, 
                         agents_role_prompt=self.agents_role_prompt, 
                         main_research_topic=self.main_research_topic, 
                         visited_urls=self.visited_urls)
        research_state.research_findings = self.research_findings
        return research_state
    
        
    async def _get_context_by_search(self):
        """
           Generates the context for the research task by searching the query and scraping the results
        Returns:
            context: List of context
        """

        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self._get_sub_queries() + [self.active_research_topic]

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self._process_sub_query(sub_query) for sub_query in sub_queries])

        return context

    async def choose_agent(self, research_topic = None):
        default_response={"agent_type":"Default Agent",
                          "agents_role_prompt":"You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text.",
                          "active_research_topic":self.active_research_topic
                          }
        try:
            choose_agent_topic = self.active_research_topic
            if research_topic:
                choose_agent_topic = research_topic
            
            llm_system_prompt = Prompts().get_prompt("choose_agent_prompt")
            llm_user_prompt = f"{self.main_research_topic} - {choose_agent_topic}" if self.main_research_topic else choose_agent_topic
            chat_response = await self.llm_provider.get_chat_response(llm_system_prompt, llm_user_prompt)
            logging.debug("choose_agent response = %s",chat_response)
            
            chat_response_json = json.loads(chat_response)
        except Exception as e:
            logging.error("Error in choose_agent WILL ATTEMPT to recover %s",e)
            chat_response_json = await self._extract_json_from_string(chat_response, default_response)
        
        self.agent_type = chat_response_json["agentType"]
        self.agents_role_prompt = chat_response_json["agentRole"]
        
        result_dict = {"agent_type":chat_response_json["agentType"],
                        "agents_role_prompt": chat_response_json["agentRole"],
                        "active_research_topic":self.active_research_topic
                        }
        return result_dict
    
    async def _extract_json_from_string(self, chat_response, default_response):
        result_json = default_response
        stack = []
        json_str = ""
        in_json = False
        
        for char in chat_response:
            if char == '{':
                stack.append(char)
                in_json = True
            if in_json:
                json_str += char
            if char == '}':
                stack.pop()
                if not stack:
                    in_json = False
                    break
    
        if json_str:
            try:
                # Attempt to parse the extracted string as JSON
                json_data = json.loads(json_str)
                result_json = json_data
            except json.JSONDecodeError:
                pass
        
        return result_json


    async def select_subtopics(self, subtopics: list = []) -> list:
        class Subtopic(BaseModel):
            task: str = Field(description="Task name", min_length=1)

        class Subtopics(BaseModel):
            subtopics: List[Subtopic] = []

        try:
            parser = PydanticOutputParser(pydantic_object=Subtopics)
            
            subtopic_prompt_template = Prompts().get_prompt("subtopics_prompt")

            prompt = PromptTemplate(
                template=subtopic_prompt_template,
                input_variables=["task", "data", "subtopics", "max_subtopics"],
                partial_variables={
                    "format_instructions": parser.get_format_instructions()},
            )

            model = self.llm_provider.llm

            chain = prompt | model | parser

            output = chain.invoke({
                "task": self.active_research_topic,
                "data": self.research_findings,
                "subtopics": subtopics,
                "max_subtopics": self.cfg.max_subtopics
            })
            subtopics_dict =  output.dict()["subtopics"]
            subtopics = [subtopic['task'] for subtopic in subtopics_dict]
        except Exception as e:
            logging.error("Error in select_subtopics %s",e)
            
        return subtopics

        
    async def _get_sub_queries(self):
        """
        Gets the sub queries
        """
        default_response = []
        chat_response_json = None
        try:
            if self.report_type == ReportType.DetailedReport.value or self.report_type == ReportType.SubtopicReport.value:
                task = f"{self.main_research_topic} - {self.active_research_topic}"
            else:
                task = self.active_research_topic
        
            search_queries_prompt = Prompts().get_prompt("search_queries_prompt",
                                                        max_iterations=self.cfg.max_iterations,
                                                        task=task,
                                                        datetime_now = datetime.now().strftime('%B %d, %Y'))

            chat_response = await self.llm_provider.get_chat_response(self.agents_role_prompt, search_queries_prompt)
            logging.debug("get_sub_queries response = %s",chat_response)

            chat_response_json = json.loads(chat_response)
            
        except Exception as e:
            logging.error("Error in get_sub_queries WILL ATTEMPT to recover %s",e)
            chat_response_json = await self._extract_json_from_string(chat_response, default_response)

        return chat_response_json


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
                scrape_content = getattr(module, scraper_nm)
                content = scrape_content(link)

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
        """ Summarize Raw Data """
        context_compressor = ContextCompressor(documents=pages, embeddings=self.cfg.embedding_provider)
        return context_compressor.get_context(query, max_results = 8)

    async def _process_sub_query(self, sub_query: str):
        """Takes in a sub query and scrapes urls based on it and gathers context."""

        scraped_sites = await self._scrape_sites_by_query(sub_query)
        content = await self._get_similar_content_by_query(sub_query, scraped_sites)
        return content
    
    # ##########################################################################################

    def get_prompt_by_report_type(self):
        report_type_mapping = {
            ReportType.ResearchReport.value: "research_report_prompt",
            ReportType.ResourceReport.value: "resource_report_prompt",
            ReportType.OutlineReport.value:  "outline_report_prompt",
            ReportType.CustomReport.value:   "custom_report_prompt", # Not Implemented
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
                    {"role": "user",   "content": report_prompt}]
            
            provider = self.cfg.llm_provider(
                            model=self.cfg.smart_llm_model,
                            temperature=deterministic_temp,
                            max_tokens=self.cfg.smart_token_limit)
            
            #report = await provider.get_chat_response(messages=messages, stream=True)
            report = await provider.get_chat_response(messages=messages)

        except Exception as e:
            print(f"Error in generate_report: {e}")

        return report

