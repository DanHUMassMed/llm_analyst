""" Test Cases for ResearchState """
import inspect
import pytest

from tests.utils_for_pytest import dump_test_results, get_resource_file_path
from llm_analyst.core.research_state import ResearchState

def setup_research_state():
    active_research_topic = "This is the active topic"                           # Passed in
    report_type           = "report_type"                                        # Passed in
    agent_type            = "This is the Agent Type"                             # Passed in
    agents_role_prompt    = "This is the Agent Prompt"                           # Passed in
    main_research_topic   = "Main Research topic"                                # Passed in
    visited_urls          = set(['https://example.com', 'https://another.com'])  # Internal
    initial_findings      = ["Research on topic 1","Research on topic 2"]        # Internal
    research_findings     = ["Research on topic 1","Research on topic 2"]        # Internal
    report_headings       = ["#Title","## Heading1","### Subheading 1"]          # Internal
    report_md             = "#Report Markdown"                                   # Internal
    final_report_md       = "Final report"                                       # Internal
    
    test_research_state = ResearchState(active_research_topic = active_research_topic,
                                   report_type = report_type,
                                   agent_type = agent_type,
                                   agents_role_prompt = agents_role_prompt,
                                   main_research_topic = main_research_topic)
    test_research_state.visited_urls =visited_urls
    test_research_state.initial_findings = initial_findings
    test_research_state.research_findings = research_findings
    test_research_state.report_headings = report_headings
    test_research_state.report_md = report_md
    test_research_state.final_report_md = final_report_md
    
    return test_research_state

def assert_all_attributes(research_state_l, research_state_r):
    assert research_state_l.active_research_topic == research_state_r.active_research_topic
    assert research_state_l.report_type == research_state_r.report_type
    assert research_state_l.agent_type == research_state_r.agent_type
    assert research_state_l.agents_role_prompt == research_state_r.agents_role_prompt
    assert research_state_l.main_research_topic == research_state_r.main_research_topic
    assert research_state_l.visited_urls == research_state_r.visited_urls
    assert research_state_l.initial_findings == research_state_r.initial_findings
    assert research_state_l.research_findings == research_state_r.research_findings
    assert research_state_l.report_headings == research_state_r.report_headings
    assert research_state_l.report_md == research_state_r.report_md
    assert research_state_l.final_report_md == research_state_r.final_report_md


    
def test_copy_of_research_state():
    """Test copy of research state = to original
    """
    function_name = inspect.currentframe().f_code.co_name
    
    test_research_state = setup_research_state()
    
    copy_of_research_state = test_research_state.copy_of_research_state()

    assert_all_attributes(test_research_state, copy_of_research_state)
    
    dump_test_results(function_name, copy_of_research_state.dump())
    
def test_dump_and_load():
    """Test dump and load ensure that data remain consistent
    """
    test_research_state = setup_research_state()
    
    test_json_file_path = get_resource_file_path("tst_research_state_2.json")
    test_research_state.dump(test_json_file_path)
    
    loaded_research_state = ResearchState.load(test_json_file_path)
    
    assert_all_attributes(test_research_state,loaded_research_state)
        
def test_dump_and_load_minimal():
    """Test dump and load ensure that data remain consistent
    """
    test_research_state = ResearchState(active_research_topic = "This is the active topic" )
    test_json_file_path = get_resource_file_path("tst_research_state_3.json")
    test_research_state.dump(test_json_file_path)

    loaded_research_state = ResearchState.load(test_json_file_path)

    assert_all_attributes(test_research_state,loaded_research_state)



if __name__ == "__main__":
    pytest.main([__file__])
