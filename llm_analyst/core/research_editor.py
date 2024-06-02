from llm_analyst.core.config import Config, ReportType
from llm_analyst.core.prompts import Prompts
from llm_analyst.utils.app_logging import trace_log, logging
from llm_analyst.core.research_state import ResearchState, DataSource
from llm_analyst.core.research_analyst import LLMAnalyst
from llm_analyst.core.research_writer import LLMWriter
from llm_analyst.utils.app_logging import logging

class LLMEditor(ResearchState):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.cfg = kwargs.get('config', Config())
        
        self.llm_provider = self.cfg.llm_provider(
            model = self.cfg.llm_model,
            temperature = self.cfg.llm_temperature,
            max_tokens = self.cfg.llm_token_limit)
        
        self.prompts = Prompts(self.cfg)

    async def create_detailed_report(self):
        llm_analyst = LLMAnalyst(config = self.cfg, **self.dump())
        primary_research = await llm_analyst.conduct_research()
        logging.debug("="*40)
        logging.debug(primary_research)
        subtopics = await llm_analyst.select_subtopics()

        for subtopic in subtopics:
            print(f"Researching {subtopic}")
            subtopic_assistant = LLMAnalyst(config = self.cfg, **primary_research.dump())
            subtopic_assistant.active_research_topic = subtopic
            subtopic_assistant.report_type = ReportType.SubtopicReport
            subtopic_assistant.main_research_topic = primary_research.active_research_topic
                        
            subtopic_research = await subtopic_assistant.conduct_research()
            subtopic_report = await subtopic_assistant.write_report()

            primary_research.research_findings = subtopic_assistant.research_findings
            primary_research.visited_urls = list(set(primary_research.visited_urls).union(subtopic_assistant.visited_urls))
            primary_research.report_md += "\n\n\n" + subtopic_report.report_md
            logging.debug(f"Writing {subtopic} research_findings=len({len(primary_research.research_findings)})")
            
        
        llm_writer = LLMWriter(config = self.cfg, **primary_research.dump())
        
        introduction = await llm_writer.write_introduction()
        toc = await llm_writer.write_table_of_contents()
        references = await llm_writer.write_references()
        primary_research.final_report_md = f"{introduction}\n\n{toc}\n\n{primary_research.report_md}\n\n{references}"
        return primary_research.copy_state()
        
        
        
        
