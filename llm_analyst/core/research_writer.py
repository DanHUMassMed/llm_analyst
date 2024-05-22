import asyncio
import time
import importlib
from datetime import datetime
import json
import warnings
import aiofiles
import urllib
import uuid
import importlib.util
import os

from md2pdf.core import md2pdf
import mistune
from docx import Document
from htmldocx import HtmlToDocx

from concurrent.futures.thread import ThreadPoolExecutor
from llm_analyst.core.config import Config, ReportType
from llm_analyst.core.prompts import Prompts
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.embedding_methods.compressor import ContextCompressor
from llm_analyst.utils.app_logging import trace_log,logging
from llm_analyst.utils.utilities import get_resource_path
from llm_analyst.utils.app_logging import trace_log,logging


class LLMWriter:
    def __init__(
        self,
        query: str,
        report_type = ReportType.ResearchReport.value,
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
        self.report_md = None

    # async def detailed_report(self):
    #     main_task_assistant = LLMResearcher(query=query, report_type=report_type)
    #     await main_task_assistant.conduct_research()
    #     global_context = main_task_assistant.context
    #     global_urls = main_task_assistant.visited_urls
    
        
  
    async def _write_md_to_file(self) -> None:
        """Asynchronously write md to a file in UTF-8 encoding.

        Args:
            filename (str): The filename to write to.
            text (str): The text to write.
        """
        file_nm = uuid.uuid4().hex
        file_path = os.path.join(self.cfg.report_out_dir, f"{file_nm}")
        if file_path[0]=='~':
            file_path = os.path.expanduser(file_path)
            
        filename = f"{file_path}.md"
        
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Convert text to UTF-8, replacing any problematic characters
        text_utf8 = self.report_md.encode('utf-8', errors='replace').decode('utf-8')

        async with aiofiles.open(filename, "w", encoding='utf-8') as file:
            await file.write(text_utf8)
            
        return file_path


    async def write_to_pdf(self) -> str:
        """Converts Markdown text to a PDF file and returns the file path.
        Returns:
            str: The encoded file path of the generated PDF.
        """
        file_path = await self._write_md_to_file()
        pdf_styles_path = os.path.join(get_resource_path(), 'pdf_styles.css')
        logging.debug("pdf_styles_path %s", pdf_styles_path)
        try:
            md2pdf(f"{file_path}.pdf",
                md_content=None,
                md_file_path=f"{file_path}.md",
                css_file_path=pdf_styles_path,
                base_url=None)
            print(f"Report written to {file_path}.pdf")
        except Exception as e:
            print(f"Error in converting Markdown to PDF: {e}")
            logging.error("Error in converting Markdown to PDF: %s", e)
            return ""

        encoded_file_path = urllib.parse.quote(f"{file_path}.pdf")
        return encoded_file_path

    async def write_to_word(self) -> str:
        """Converts Markdown text to a DOCX file and returns the file path.

        Returns:
            str: The encoded file path of the generated DOCX.
        """
        file_path = await self._write_md_to_file()

        try:
            # Convert report markdown to HTML
            html = mistune.html(self.report_md)
            # Create a document object
            doc = Document()
            HtmlToDocx().add_html_to_document(html, doc)

            # Saving the docx document to file_path
            doc.save(f"{file_path}.docx")
            
            print(f"Report written to {file_path}.docx")

            encoded_file_path = urllib.parse.quote(f"{file_path}.docx")
            return encoded_file_path
        
        except Exception as e:
            print(f"Error in converting Markdown to DOCX: {e}")
            return ""
