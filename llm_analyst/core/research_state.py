""" Object to maintain the Reseach state as it progressess"""
from llm_analyst.core.config import ReportType
from llm_analyst.core.exceptions import LLMAnalystsException

class ResearchState:
    def __init__(self, **kwargs):
        self.active_research_topic = kwargs.get('active_research_topic', None)
        if not self.active_research_topic:
            raise LLMAnalystsException("active_research_topic is a required field")
        
        self.report_type         = kwargs.get('report_type', ReportType.ResearchReport.value)
        self.agent_type          = kwargs.get('agent_type', None)
        self.agents_role_prompt  = kwargs.get('agents_role_prompt', None)
        self.main_research_topic = kwargs.get('main_research_topic', "")
        self.visited_urls        = kwargs.get('visited_urls', set())
        
        self.initial_findings  = []
        self.research_findings = []
        self.report_headings   = []
        self.report_md         = ""
        self.final_report_md   = ""
       
        
    def __str__(self):
        ret_val = ""
        ret_val +=f"active_research_topic  = {self.active_research_topic}\n"
        ret_val +=f"main_research_topic    = {self.main_research_topic}\n"
        ret_val +=f"Visited URLs length    = {len(self.visited_urls)}\n"
        ret_val +=f"Reseach finding length = {len(self.research_findings)}\n"
        ret_val +=f"Report headings length = {len(self.report_headings)}\n"
        ret_val +=f"Markdown report length = {len(self.report_md)}\n"
        ret_val +=f"agent_type             = {self.agent_type}\n"
        ret_val +=f"agents_role_prompt     = {self.agents_role_prompt}\n"
        return ret_val
    
    def copy_of_research_state(self):
        research_state = ResearchState(active_research_topic=self.active_research_topic, 
                         report_type=self.report_type, 
                         agent_type=self.agent_type, 
                         agents_role_prompt=self.agents_role_prompt, 
                         main_research_topic=self.main_research_topic, 
                         visited_urls=self.visited_urls)
        research_state.initial_findings = self.initial_findings
        research_state.research_findings = self.research_findings
        research_state.report_headings = self.report_headings
        research_state.report_md = self.report_md
        research_state.final_report_md = self.final_report_md
        return research_state
    
    

