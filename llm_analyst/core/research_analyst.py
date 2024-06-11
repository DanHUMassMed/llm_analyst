import asyncio
import importlib
from datetime import datetime
import json
import warnings
from concurrent.futures.thread import ThreadPoolExecutor
from llm_analyst.core.config import Config, ReportType, DataSource
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.embedding_methods.compressor import ContextCompressor
from llm_analyst.utils.app_logging import logging
from llm_analyst.core.research_state import ResearchState
from llm_analyst.documents.document import DocumentLoader 
from llm_analyst.documents.vector_store import VectorStore
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from typing import List
from pydantic import BaseModel, Field

class LLMAnalyst(ResearchState):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.cfg = kwargs.get('config', Config())
        
        self.llm_provider = self.cfg.llm_provider(
            model = self.cfg.llm_model,
            temperature = self.cfg.llm_temperature,
            max_tokens = self.cfg.llm_token_limit)
        
        self.prompts = Prompts(self.cfg)

        
    async def conduct_research(self):
        """The Analysts main task is to conduct research"""
        if not (self.agent_type):
            await self.choose_agent()
        
        match self.data_source:
            case DataSource.Web:
                self.research_findings = await self._research_by_internet_search()
            case DataSource.LocalStore:
                self.research_findings = await self._research_by_local_store_search()
            case DataSource.SelectURLs:
                self.research_findings = await self._research_by_custom_urls()
            case _:
                err_msg="ERROR: Unkown DataSource {self.data_source} in LLMAnalyst.conduct_research()"
                logging.error(err_msg)
                raise LLMAnalystsException(err_msg)
        
        if not self.initial_findings:
            self.initial_findings = self.research_findings
            
        return self.copy_state()
        
    async def choose_agent(self, research_topic = None):
        """ Given an active_research_topic 
            1. Find an appropriate type of Reseacher (Agent) to do the work
            2. Note: The prompt that is returned is used to guide the LLM
        """
        default_response={"agent_type":"Default Agent",
                          "agents_role_prompt":"You are an AI critical thinker research assistant. Your sole purpose is to write well written, critically acclaimed, objective and structured reports on given text.",
                          "active_research_topic":self.active_research_topic
                          }
        try:
            choose_agent_topic = self.active_research_topic
            if research_topic:
                choose_agent_topic = research_topic
            
            llm_system_prompt = self.prompts.get_prompt("choose_agent_prompt")
            llm_user_prompt = f"{self.main_research_topic} - {choose_agent_topic}" if self.main_research_topic else choose_agent_topic
            chat_response = await self.llm_provider.get_chat_response(llm_system_prompt, llm_user_prompt)
            logging.debug("PROMPT choose_agent response = %s",chat_response)
            
            chat_response_json = json.loads(chat_response)
        except Exception as e:
            logging.error("Error in choose_agent WILL ATTEMPT to recover %s",e)
            chat_response_json = await self._extract_json_from_string(chat_response, default_response)
        
        self.agent_type = chat_response_json["agentType"]
        self.agents_role_prompt = chat_response_json["agentRole"]
        research_state = ResearchState(active_research_topic = self.active_research_topic,
                                       report_type = self.report_type,
                                       agent_type = self.agent_type,
                                       agents_role_prompt = self.agents_role_prompt)
        return research_state
    
        
    async def _research_by_internet_search(self):
        """ Given an active_research_topic 
            1. Find a list of related subtopic to search. (LLM)
            2. For each subtopic find a list of URLs. (Search Engine)
            3. For each URL scrape the web site for content.
        """
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self._get_sub_queries() + [self.active_research_topic]

        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self._process_internet_query(sub_query) for sub_query in sub_queries])
        return context

    async def _process_internet_query(self, sub_query: str):
        """Takes in a sub query and scrapes urls based on it and gathers context."""
        scraped_sites = await self._scrape_sites_by_query(sub_query)
        content = await self._get_similar_content_by_query(sub_query, scraped_sites)
        return content

    async def _research_by_local_store_search(self):
        """ Given an active_research_topic 
            1. Find a list of related subtopic to search. (LLM)
            2. For each topic exctract similar data from local store
        """
        
        vector_store = await VectorStore.create(self.cfg.cache_dir, self.cfg.local_store_dir)
        context = []
        # Generate Sub-Queries including original query
        sub_queries = await self._get_sub_queries()
        
        # Using asyncio.gather to process the sub_queries asynchronously
        context = await asyncio.gather(*[self._process_local_store_query(sub_query, vector_store) for sub_query in sub_queries])

        return context

    async def _process_local_store_query(self, sub_query, vector_store):
        """Takes in a sub query and gathers context from the local store."""
        # document_data = await self._get_docs_by_query(sub_query)
        pages = await vector_store.retrieve_pages_for_query(sub_query)
        context_compressor = ContextCompressor(documents=pages, embeddings=self.cfg.embedding_provider)
        content = context_compressor.get_context(sub_query, max_results = 8)
        await self._keep_unique_urls(context_compressor.unique_documets_visited)
        return content

    async def _research_by_custom_urls(self):
        """
            Scrapes and compresses the context from the given urls
        """
        new_search_urls = await self._keep_unique_urls(self.custom_search_urls)
        scraped_sites = self._scrape_urls(new_search_urls)
        return await self._get_similar_content_by_query(self.active_research_topic, scraped_sites)


    async def _get_sub_queries(self):
        """
        Given an active_research_topic
        Request a list of sub queries that could appropraitly answer the active_research_topic
        """
        default_response = []
        sub_queries = None
        try:
            if self.report_type == ReportType.DetailedReport or self.report_type == ReportType.SubtopicReport:
                task = f"{self.main_research_topic} - {self.active_research_topic}"
            else:
                task = self.active_research_topic
        
            search_queries_prompt = self.prompts.get_prompt("search_queries_prompt",
                                                        max_iterations=self.cfg.max_iterations,
                                                        task=task,
                                                        datetime_now = datetime.now().strftime('%B %d, %Y'))

            chat_response = await self.llm_provider.get_chat_response(self.agents_role_prompt, search_queries_prompt)
            logging.debug("PROMPT get_sub_queries response = %s",chat_response)

            sub_queries = json.loads(chat_response)
            
        except Exception as e:
            logging.error("Error in get_sub_queries WILL ATTEMPT to recover %s", e)
            sub_queries = await self._extract_json_from_string(chat_response, default_response)

        if self.report_type != ReportType.SubtopicReport:
            sub_queries.append(self.active_research_topic)
            
        return sub_queries


    async def _keep_unique_urls(self, url_set_input):
        """ Parse the URLS and remove any duplicates
        """
        new_urls = []
        
        for url in url_set_input:
            if url not in self.visited_urls:
                self.visited_urls.append(url)
                new_urls.append(url)

        return new_urls


    async def _extract_json_from_string(self, chat_response, default_response):
        """Helper method
            In some case the requested JSON response from the LLM is wrapped in explainitory text
            this method attempts to extract JSON from the LLM ressponse
        """
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
        default_response = []
        sub_queries = None
        try:
            format_instructions="You MUST respond with a list of strings in the following format: [\"subtopic 1\", \"subtopic 2\", \"subtopic 3\"]. The response should contain ONLY the list."
            
            subtopics_prompt = self.prompts.get_prompt("subtopics_prompt",
                                                        task = self.active_research_topic,
                                                        data = self.research_findings,
                                                        subtopics = subtopics,
                                                        max_subtopics=self.cfg.max_subtopics,
                                                        format_instructions = format_instructions)

            chat_response = await self.llm_provider.get_chat_response(self.agents_role_prompt, subtopics_prompt)
            logging.debug("PROMPT get_sub_queries response = %s",chat_response)

            sub_queries = json.loads(chat_response)
            
        except Exception as e:
            logging.error("Error in get_sub_queries WILL ATTEMPT to recover %s", e)
            sub_queries = await self._extract_json_from_string(chat_response, default_response)

        if self.report_type != ReportType.SubtopicReport:
            sub_queries.append(self.active_research_topic)
            
        return sub_queries


    # async def select_subtopics(self, subtopics: list = []) -> list:
    #     """Used for detailed research 
    #        Select related subtopics from the main research topic
    #        Note: Here we are esentially defining an "outline" for the research to be conducted  
    #     """
    #     class Subtopic(BaseModel):
    #         task: str = Field(description="Task name", min_length=1)

    #     class Subtopics(BaseModel):
    #         subtopics: List[Subtopic] = []

    #     try:
    #         parser = PydanticOutputParser(pydantic_object=Subtopics)
            
    #         subtopic_prompt_template = self.prompts.get_prompt("subtopics_prompt")

    #         prompt = PromptTemplate(
    #             template=subtopic_prompt_template,
    #             input_variables=["task", "data", "subtopics", "max_subtopics"],
    #             partial_variables={
    #                 "format_instructions": parser.get_format_instructions()},
    #         )
    #         logging.debug("PROMPT select_subtopics prompt= %s", prompt)
    #         logging.debug("PROMPT select_subtopics format_instructions= %s", parser.get_format_instructions())
    #         model = self.llm_provider.llm

    #         chain = prompt | model | parser

    #         output = chain.invoke({
    #             "task": self.active_research_topic,
    #             "data": self.research_findings,
    #             "subtopics": subtopics,
    #             "max_subtopics": self.cfg.max_subtopics
    #         })
    #         subtopics_dict =  output.dict()["subtopics"]
    #         subtopics = [subtopic['task'] for subtopic in subtopics_dict]
    #         logging.debug("PROMPT select_subtopics output=%s", output)
    #     except Exception as e:
    #         logging.error("Error in select_subtopics %s", e)
            
    #     return subtopics

        

    def _scrape_urls(self, urls):
        """
        Given a list of URLs
        1. Determine an appropriate scraper based on URL content
        2. For each URL Scrape the website and aggragate the content into a list of strings
           one for each site
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
        """Given a sub_query
           1. Call the configured internet search provider and retrieve a list of URLs
           2. Keep only the Unique URLs
           3. Scrape the proved site for content
        """
        search_results = self.cfg.internet_search(sub_query, max_results=self.cfg.max_search_results_per_query)
        new_search_urls = await self._keep_unique_urls([url.get("href") for url in search_results])
        scraped_content_results = self._scrape_urls(new_search_urls)
        return scraped_content_results

    async def _get_similar_content_by_query(self, query, pages):
        """ Instead of immediately returning retrieved documents as-is, 
            they are compressed using the context of the given query, 
            then only the relevant information is returned. """
        context_compressor = ContextCompressor(documents=pages, embeddings=self.cfg.embedding_provider)
        return context_compressor.get_context(query, max_results = 8)

    
    # ##########################################################################################

    async def write_report(self):
        """
        Generate a report based on the report_type specified
        """
        report_prompt_nm = f"{self.report_type.value}_prompt"
        report_format = 'APA'
        datetime_now = datetime.now().strftime('%B %d, %Y')
        
        if self.report_type == ReportType.CustomReport:
            raise LLMAnalystsException("CUSTOM REPORT Not Implemented")
        elif self.report_type == ReportType.SubtopicReport:
            report_prompt = self.prompts.get_prompt(report_prompt_nm,
                                            context=self.research_findings,
                                            current_subtopic=self.active_research_topic,
                                            main_topic=self.main_research_topic,
                                            max_subsections=self.cfg.max_subsections,
                                            report_format=report_format,
                                            existing_headers=self.report_headings,
                                            datetime_now=datetime_now,
                                            total_words=self.cfg.total_words)
        else:
            report_prompt = self.prompts.get_prompt(report_prompt_nm,
                                             context=self.research_findings,
                                             question=self.active_research_topic,
                                             total_words=self.cfg.total_words,
                                             report_format=report_format,
                                             datetime_now = datetime_now)

        try:
            
            chat_response = await self.llm_provider.get_chat_response(self.agents_role_prompt, report_prompt)
            logging.debug("PROMPT write_report response = %s",chat_response)
            self.report_md  = chat_response
            
        except Exception as e:
            print(f"Error in generate_report: {e}")

        return self.copy_state()

