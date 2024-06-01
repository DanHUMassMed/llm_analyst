""" Test Cases for ResearchState """
import inspect
import pytest

from tests.utils_for_pytest import dump_test_results, get_resource_file_path
from llm_analyst.core.research_state import ResearchState

def setup_research_state():
    active_research_topic = "This is the active topic"
    report_type           = "report_type"
    agent_type            = "This is the Agent Type"   
    data_source            = "web"                             
    agents_role_prompt    = "This is the Agent Prompt"                          
    main_research_topic   = "Main Research topic"                                
    visited_urls          = ['https://example.com', 'https://another.com'] 
    initial_findings      = ["Research on topic 1","Research on topic 2"]        
    research_findings     = ["Research on topic 1","Research on topic 2"]        
    report_headings       = ["#Title","## Heading1","### Subheading 1"]          
    report_md             = "#Report Markdown"                                   
    final_report_md       = "Final report"                                       
    
    test_research_state = ResearchState(active_research_topic = active_research_topic,
                                        report_type = report_type,
                                        agent_type = agent_type,
                                        data_source = data_source,
                                        agents_role_prompt = agents_role_prompt,
                                        main_research_topic = main_research_topic,
                                        visited_urls =visited_urls,
                                        initial_findings = initial_findings,
                                        research_findings = research_findings,
                                        report_headings = report_headings,
                                        report_md = report_md,
                                        final_report_md = final_report_md)
    
    return test_research_state

def assert_all_attributes(research_state_l, research_state_r):
    assert research_state_l.active_research_topic == research_state_r.active_research_topic
    assert research_state_l.report_type == research_state_r.report_type
    assert research_state_l.agent_type == research_state_r.agent_type
    assert research_state_l.data_source == research_state_r.data_source
    assert research_state_l.agents_role_prompt == research_state_r.agents_role_prompt
    assert research_state_l.main_research_topic == research_state_r.main_research_topic
    assert research_state_l.visited_urls == research_state_r.visited_urls
    assert research_state_l.initial_findings == research_state_r.initial_findings
    assert research_state_l.research_findings == research_state_r.research_findings
    assert research_state_l.report_headings == research_state_r.report_headings
    assert research_state_l.report_md == research_state_r.report_md
    assert research_state_l.final_report_md == research_state_r.final_report_md

    
def test_dump_and_load():
    """Test dump and load ensure that data remain consistent
    """
    test_research_state = setup_research_state()
    
    test_json_file_path = get_resource_file_path("tst_research_state_2.json")
    test_research_state.dump(test_json_file_path)
    
    
    loaded_research_state = ResearchState.load(test_json_file_path)
    
    assert_all_attributes(test_research_state, loaded_research_state)
        
def test_dump_and_load_minimal():
    """Test dump and load ensure that data remain consistent
    """
    test_research_state = ResearchState(active_research_topic = "This is the active topic" )
    test_json_file_path = get_resource_file_path("tst_research_state_3.json")
    test_research_state.dump(test_json_file_path)

    loaded_research_state = ResearchState.load(test_json_file_path)

    assert_all_attributes(test_research_state,loaded_research_state)

def test_copy_research_state():
    test_research_state = setup_research_state()
    copy_of_research_state = test_research_state.copy_state()
    
    assert_all_attributes(test_research_state, copy_of_research_state)
    

if __name__ == "__main__":
    pytest.main([__file__])
