from datetime import datetime
import markdown

from md2pdf.core import md2pdf
import mistune
from docx import Document
from htmldocx import HtmlToDocx

from llm_analyst.core.config import Config, ReportType
from llm_analyst.core.prompts import Prompts
from llm_analyst.utils.utilities import get_resource_path
from llm_analyst.utils.app_logging import trace_log,logging
from llm_analyst.core.research_state import ResearchState, DataSource



class LLMWriter(ResearchState):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.cfg = kwargs.get('config', Config())
        
        self.llm_provider = self.cfg.llm_provider(
            model = self.cfg.llm_model,
            temperature = self.cfg.llm_temperature,
            max_tokens = self.cfg.llm_token_limit)
        
        self.prompts = Prompts(self.cfg)
            
    def _extract_headers(self):
        # Function to extract headers from markdown text

        headers = []
        parsed_md = markdown.markdown(self.report_md)  # Parse markdown text
        lines = parsed_md.split("\n")  # Split text into lines

        stack = []  # Initialize stack to keep track of nested headers
        for line in lines:
            if line.startswith("<h") and len(line) > 1:  # Check if the line starts with an HTML header tag
                #level = int(line[2])  # Extract header level
                level = line[2] if line[2].isdigit() else 0
                header_text = line[
                    line.index(">") + 1: line.rindex("<")
                ]  # Extract header text

                # Pop headers from the stack with higher or equal level
                while stack and stack[-1]["level"] >= level:
                    stack.pop()

                header = {
                    "level": level,
                    "text": header_text,
                }  # Create header dictionary
                if stack:
                    stack[-1].setdefault("children", []).append(
                        header
                    )  # Append as child if parent exists
                else:
                    # Append as top-level header if no parent exists
                    headers.append(header)

                stack.append(header)  # Push header onto the stack

        return headers  # Return the list of headers
    
    async def write_introduction(self):
        report_intro = ""
        try:
            report_introduction_prompt = self.prompts.get_prompt("report_introduction",
                                                     question=self.active_research_topic,
                                                     research_summary=self.initial_findings,
                                                     datetime_now = datetime.now().strftime('%B %d, %Y'))
            report_intro = await self.llm_provider.get_chat_response(self.agents_role_prompt, report_introduction_prompt)
            logging.debug("PROMPT write_introduction response = %s",report_intro)
            
        except Exception as e:
            logging.error("Error in generating report introduction: %s",e)

        return report_intro

    async def write_table_of_contents(self):
        try:
            # Function to generate table of contents recursively
            def generate_table_of_contents(headers, indent_level=0):
                toc = ""  # Initialize table of contents string
                for header in headers:
                    toc += (
                        " " * (indent_level * 4) + "- " + header["text"] + "\n"
                    )  # Add header text with indentation
                    if "children" in header:  # If header has children
                        toc += generate_table_of_contents(
                            header["children"], indent_level + 1
                        )  # Generate TOC for children
                return toc  # Return the generated table of contents

            # Extract headers from markdown text
            headers = self._extract_headers()
            toc = "## Table of Contents\n\n" 
            toc += generate_table_of_contents(headers)  # Generate table of contents

            return toc  # Return the generated table of contents

        except Exception as e:
            logging.error("Error in generating table_of_contents: %s",e)
            return "" 

    async def write_references(self):
        """
        This function create a reference section based on kown URLs that have been visited
        """
        try:
            url_markdown = "\n\n\n## References\n\n"

            url_markdown += "".join(f"- [{url}]({url})\n" for url in self.visited_urls)

            return url_markdown

        except Exception as e:
            print(f"Encountered exception in adding source urls : {e}")
            return ""
        
 