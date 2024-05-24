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
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_writer import LLMWriter

class LLMEditor(ResearchState):
    def __init__(
        self,
        active_research_topic: str,
        config = Config(),
        report_type = ReportType.ResearchReport.value,
        agent_type = None,
        agents_role_prompt = None,
        main_research_topic = "",
        visited_urls = set()
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

    @classmethod
    def init(self,research_state):
        llm_analyst = LLMEditor(active_research_topic=research_state.active_research_topic,
                         report_type=research_state.report_type,
                         agent_type=research_state.agent_type,
                         agents_role_prompt=research_state.agents_role_prompt,
                         main_research_topic=research_state.main_research_topic,
                         visited_urls=research_state.visited_urls)
        llm_analyst.research_findings = research_state.research_findings
        llm_analyst.report_headings = research_state.report_headings
        llm_analyst.report_md = research_state.report_md
        return llm_analyst

    async def create_detailed_report(self):
        llm_analyst = LLMAnalyst(self.active_research_topic, config = self.cfg)
        primary_research = await llm_analyst.conduct_research()
        print("="*40)
        print(primary_research)
        subtopics = await llm_analyst.select_subtopics()

        for subtopic in subtopics:
            print(f"Researching {subtopic}")
            subtopic_assistant = LLMAnalyst(
                active_research_topic = subtopic,
                report_type = "subtopic_report",
                main_research_topic = primary_research.active_research_topic,
                visited_urls = primary_research.visited_urls,
                agents_role_prompt =  primary_research.agents_role_prompt,
                agent_type = primary_research.agent_type
            )
            subtopic_assistant.research_findings = primary_research.research_findings
            subtopic_assistant.report_headings = primary_research.report_headings
            
            subtopic_research = await subtopic_assistant.conduct_research()
            print(f"Writing {subtopic}")
            subtopic_report = await subtopic_assistant.write_report()

            primary_research.research_findings = subtopic_assistant.research_findings
            primary_research.visited_urls.update(subtopic_assistant.visited_urls)
            primary_research.report_md += "\n\n\n" + subtopic_report.report_md
            
        
        introduction = await LLMWriter.init(primary_research).write_introduction()
        toc = await LLMWriter.init(primary_research).write_table_of_contents()
        references = await LLMWriter.init(primary_research).write_references()
        primary_research.final_report_md = f"{introduction}\n\n{toc}\n\n{primary_research.report_md}\n\n{references}"
        return primary_research.copy_of_research_state()
        
        
        
        
