""" Object to maintain the Reseach state as it progressess"""
import json
import copy
from enum import Enum
from llm_analyst.core.config import Config, ReportType, DataSource
from llm_analyst.core.exceptions import LLMAnalystsException

class ResearchState:
    def __init__(self, **kwargs):
        self.active_research_topic = kwargs.get('active_research_topic', None)
        #if not self.active_research_topic:
        #    raise LLMAnalystsException("active_research_topic is a required field")
        
        self.report_type         = kwargs.get('report_type', ReportType.ResearchReport)
        self.agent_type          = kwargs.get('agent_type', None)
        self.data_source         = kwargs.get('data_source', DataSource.Web)
        self.agents_role_prompt  = kwargs.get('agents_role_prompt', None)
        self.main_research_topic = kwargs.get('main_research_topic', "")
                
        self.custom_search_urls  = kwargs.get('custom_search_urls', [])
        self.visited_urls        = kwargs.get('visited_urls', [])
        self.initial_findings    = kwargs.get('initial_findings', [])
        self.research_findings   = kwargs.get('research_findings', [])
        self.report_headings     = kwargs.get('report_headings', [])
        self.report_md           = kwargs.get('report_md', "")
        self.final_report_md     = kwargs.get('final_report_md', "")
        
    def __str__(self):
        ret_val = ""
        ret_val +=f"active_research_topic  = {self.active_research_topic}\n"
        ret_val +=f"main_research_topic    = {self.main_research_topic}\n"
        ret_val +=f"report_type            = {self.report_type}\n"
        ret_val +=f"data_source            = {self.data_source}\n"
        ret_val +=f"Visited URLs length    = {len(self.visited_urls)}\n"
        ret_val +=f"Reseach finding length = {len(self.research_findings)}\n"
        ret_val +=f"Report headings length = {len(self.report_headings)}\n"
        ret_val +=f"Markdown report length = {len(self.report_md)}\n"
        ret_val +=f"Final report    length = {len(self.final_report_md)}\n"
        ret_val +=f"agent_type             = {self.agent_type}\n"
        ret_val +=f"agents_role_prompt     = {self.agents_role_prompt}\n"
        return ret_val
    
    
    @classmethod
    def load(cls, research_state_file_nm):
        
        def as_enum(deserialize_obj):
            if "__enum__" in deserialize_obj:
                name, member = deserialize_obj["__enum__"].split(".")
                return getattr(globals()[name], member)
            return deserialize_obj

        research_state = None
        try:
            with open(research_state_file_nm, 'r', encoding="utf-8") as file:
                research_state_json = json.load(file, object_hook=as_enum)
                research_state = ResearchState()
                research_state.__dict__.update(research_state_json)
            
        except Exception:
            raise LLMAnalystsException("Failed to load ResearchState from json file [%s]", research_state_file_nm)
        
        return research_state
        
    def dump(self, research_state_file_nm=None):
              
        class EnumEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Enum):
                    return {"__enum__": str(obj)}
                return json.JSONEncoder.default(self, obj)
    
        base_class_attrs = vars(ResearchState())
        current_attrs = vars(self)
        research_state_json = {key: value for key, value in current_attrs.items() if key in base_class_attrs}
        
        try:
            if research_state_file_nm:
                with open(research_state_file_nm, 'w', encoding="utf-8") as file:
                    json.dump(research_state_json, file, indent=4, cls=EnumEncoder)
                    
        except Exception:
            raise LLMAnalystsException("Failed to dump ResearchState to json file [%s]", research_state_file_nm)

        return research_state_json
    
    def copy_state(self):
        """Copy of the current state"""
        return copy.copy(self)

        
        
        

        
