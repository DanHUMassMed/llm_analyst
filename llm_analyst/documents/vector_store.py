"""
This module provides the `VectorStore` class for managing a vector database 
with document embedding capabilities.
"""
import hashlib
import os
import re

from langchain_huggingface import HuggingFaceEmbeddings


from langchain_chroma import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_text_splitters import CharacterTextSplitter


from llm_analyst.documents.document import DocumentLoader
from llm_analyst.core.exceptions import LLMAnalystsException
from llm_analyst.utils.app_logging import logging


class VectorStore:

    def __init__(self, cache_directory, local_data_directory=None):
        self.cache_directory = cache_directory
        self.persist_directory = f"{cache_directory}/chroma_db"
        self.local_data_directory = local_data_directory
        self.local_db_hash = self._stored_db_hash()

        self.embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        if not os.path.exists(self.persist_directory):
            os.makedirs(self.persist_directory)
            
        self.vector_db = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
            )
            

        
    async def async_init(self):
        # Asynchronous initialization
        if self.local_data_directory:
            local_db_hash = self._local_db_hash()
            if self.local_db_hash is None or local_db_hash != self.local_db_hash:
                self.local_db_hash = local_db_hash
                document_loader = DocumentLoader(self.local_data_directory)
                documents = await document_loader.load_local_documents()
                if not documents:
                    raise LLMAnalystsException(
                        f"ERROR: No Documents loaded! Check the config local_data_directory {self.local_data_directory}"
                    )
                text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
                chunked_documents = text_splitter.split_documents(documents)
                self.vector_db = await Chroma.afrom_documents(
                                                    chunked_documents,
                                                    self.embedding_function,
                                                    persist_directory=self.persist_directory,
                                                )
                self.__store_db_hash()
            else:
                logging.info("*** Using Cached Repo. ***")

            

    @classmethod
    async def create(cls, cache_directory, local_data_directory=None):
        instance = cls(cache_directory, local_data_directory)
        await instance.async_init()
        return instance
    
    def __compute_hash(self, directory_path):
        """Compute a single SHA-256 hash for the entire directory."""
        hasher = hashlib.sha256()

        for root, dirs, files in os.walk(directory_path):
            for file_name in sorted(files):  # Sort files to ensure consistent order
                file_path = os.path.join(root, file_name)
                with open(file_path, "rb") as file:
                    buffer = file.read()
                    hasher.update(buffer)
                    hasher.update(file_path.encode())  # Include file path in hash

        return hasher.hexdigest()

    def _local_db_hash(self):
        return self.__compute_hash(self.local_data_directory)

    def __store_db_hash(self):
        """Save the hash to a file."""
        hash_file = os.path.join(self.cache_directory, "local_data_directory.sha")

        # Ensure the directory exists
        if not os.path.exists(self.cache_directory):
            os.makedirs(self.cache_directory)

        try:
            with open(hash_file, "w", encoding="utf-8") as file:
                file.write(self.local_db_hash)
        except IOError as e:
            logging.error(f"Failed to write hash to {hash_file}: {e}")

    def _stored_db_hash(self):
        ret_val = None
        hash_file = f"{self.cache_directory}/local_data_directory.sha"
        if os.path.exists(hash_file):
            with open(hash_file, "r", encoding="utf-8") as file:
                ret_val = file.read().strip()
        return ret_val

    async def retrieve_docs_for_query(self, query, max_docs=6, score_threshold=0.2):
        # The returned distance score is cosine distance. Therefore, a lower score is better.
        # Note currently not using the score but it could be useful later
        docs = await self.vector_db.asimilarity_search_with_score(query, k=max_docs)
        if docs:
            docs = [doc[0] for doc in docs]
        return docs

    def _format_url(self, source_nm):
        pub_med_ref = r"^PM\d+\.txt$"
        pub_med_central_ref = r"^PMC\d+\.txt$"
        if bool(re.match(pub_med_ref, source_nm)):
            url = f"https://pubmed.ncbi.nlm.nih.gov/{source_nm[2:-4]}/"
        elif bool(re.match(pub_med_central_ref, source_nm)):
            url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{source_nm[:-4]}/"
        else:
            url = source_nm
        return url

    async def retrieve_pages_for_query(self, query, max_docs=6, score_threshold=0.2):

        docs = await self.retrieve_docs_for_query(query, max_docs, score_threshold)
        ret_pages = []
        for page in docs:
            if page.page_content:
                url = self._format_url(os.path.basename(page.metadata["source"]))
                ret_pages.append({"raw_content": page.page_content, "url": url})

        if not ret_pages:
            raise ValueError("🤷 Failed to load any documents!")

        return ret_pages
