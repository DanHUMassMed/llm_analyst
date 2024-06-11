import asyncio
import os
import re

from langchain_community.document_loaders import (
    PyMuPDFLoader, 
    TextLoader, 
    UnstructuredCSVLoader, 
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader, 
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader
)


class DocumentLoader:

    def __init__(self, path):
        self.path = path

    def _format_url(self, source_nm):
        pub_med_ref = r'^PM\d+\.txt$'
        pub_med_central_ref = r'^PMC\d+\.txt$'
        if bool(re.match(pub_med_ref, source_nm)):
            url = f"https://pubmed.ncbi.nlm.nih.gov/{source_nm[2:-4]}/"
        elif bool(re.match(pub_med_central_ref, source_nm)):
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{source_nm[:-4]}/"
        else:
            url = source_nm
        return url

    async def load(self) -> list:
        docs_list = await self.load_documents()

        docs_gpt = []
        for doc in docs_list:
            if doc.page_content:
                url = self._format_url(os.path.basename(doc.metadata['source']))
                docs_gpt.append({
                    "raw_content": doc.page_content,
                    "url": url
                })
                    
        if not docs_gpt:
            raise ValueError("🤷 Failed to load any documents!")
        return docs_gpt

    async def load_documents(self) -> list:
        file_paths = []
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name, file_extension_with_dot = os.path.splitext(file_path)
                file_extension = file_extension_with_dot.strip(".")
                file_paths.append((file_path, file_extension))
                
        docs = await asyncio.gather(*[self._load_document(file_path_tuple[0], file_path_tuple[1]) for file_path_tuple in file_paths])
        flattened_list = [item for sublist in docs for item in sublist]
        return flattened_list

    async def _load_document(self, file_path: str, file_extension: str) -> list:
        ret_data = []
        try:
            loader_dict = {
                "pdf":  PyMuPDFLoader(file_path),
                "txt":  TextLoader(file_path),
                "doc":  UnstructuredWordDocumentLoader(file_path),
                "docx": UnstructuredWordDocumentLoader(file_path),
                "pptx": UnstructuredPowerPointLoader(file_path),
                "csv":  UnstructuredCSVLoader(file_path, mode="elements"),
                "xls":  UnstructuredExcelLoader(file_path, mode="elements"),
                "xlsx": UnstructuredExcelLoader(file_path, mode="elements"),
                "md":   UnstructuredMarkdownLoader(file_path)
            }

            loader = loader_dict.get(file_extension, None)
            if loader:
                ret_data = loader.load()

        except Exception as e:
            print(f"Failed to load document : {file_path}")
            print(e)
            
        return ret_data
