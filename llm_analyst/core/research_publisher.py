from datetime import datetime
import aiofiles
import urllib
import uuid
import os

from md2pdf.core import md2pdf
import mistune
from docx import Document
from htmldocx import HtmlToDocx

from llm_analyst.core.config import Config, ReportType, DataSource
from llm_analyst.core.prompts import Prompts
from llm_analyst.utils.app_logging import trace_log,logging
from llm_analyst.utils.utilities import get_resource_path

from llm_analyst.core.research_state import ResearchState

class LLMPublisher(ResearchState):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.cfg = kwargs.get('config', Config())
        
        self.llm_provider = self.cfg.llm_provider(
            model = self.cfg.llm_model,
            temperature = self.cfg.llm_temperature,
            max_tokens = self.cfg.llm_token_limit)
        
        self.prompts = Prompts(self.cfg)
  
    def _get_file_path(self):
        #file_nm = uuid.uuid4().hex
        now = datetime.now()
        formatted_date_time = now.strftime('%Y-%m-%d-%H%M%S%f')[:-2]
        file_nm = f"Research-{formatted_date_time}"
        file_path = os.path.join(self.cfg.report_out_dir, f"{file_nm}")
        if file_path[0]=='~':
            file_path = os.path.expanduser(file_path)
        return file_path
        
    async def publish_to_md_file(self) -> None:
        """Asynchronously write md to a file in UTF-8 encoding.

        Args:
            filename (str): The filename to write to.
            text (str): The text to write.
        """
        file_path = self._get_file_path()
        filename = f"{file_path}.md"
        
        directory = os.path.dirname(filename)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Convert text to UTF-8, replacing any problematic characters
        if self.final_report_md:
            report_to_publish = self.final_report_md
        else:
            report_to_publish = self.report_md
            
        text_utf8 = report_to_publish.encode('utf-8', errors='replace').decode('utf-8')
        async with aiofiles.open(filename, "w", encoding='utf-8') as file:
            await file.write(text_utf8)
            
        return file_path


    async def publish_to_pdf_file(self) -> str:
        """Converts Markdown text to a PDF file and returns the file path.
        Returns:
            str: The encoded file path of the generated PDF.
        """
        file_path = await self.publish_to_md_file()
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

    async def publish_to_word_file(self) -> str:
        """Converts Markdown text to a DOCX file and returns the file path.

        Returns:
            str: The encoded file path of the generated DOCX.
        """
        file_path = await self.publish_to_md_file()

        try:
            # Convert report markdown to HTML
            if self.final_report_md:
                report_to_publish = self.final_report_md
            else:
                report_to_publish = self.report_md
            
            html = mistune.html(report_to_publish)
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
