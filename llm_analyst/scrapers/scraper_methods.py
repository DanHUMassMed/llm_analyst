from langchain_community.retrievers.arxiv import ArxivRetriever
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.document_loaders.web_base import WebBaseLoader
import requests

import uuid
import re
import os



def arxiv_scraper(link):
    query = link.split("/")[-1]
    retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=None)
    docs = retriever.invoke(query)
    # Just pulling the abstract
    return docs[0].page_content

def pdf_scraper(link):
    loader = PyMuPDFLoader(link)
    docs = loader.load()
    content =""
    for doc in docs:
        content += doc.page_content
    return content

def bs_scraper(link):
    response = requests.get(link, timeout=10)
    temp_file = f"temp_{uuid.uuid4()}.html"
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(response.text)
    # Load it with an HTML parser
    loader = BSHTMLLoader(temp_file)
    document = loader.load()[0]
    if os.path.exists(temp_file):
        os.remove(temp_file)

    document.page_content = re.sub("\n\n+", "\n", document.page_content)
    return document.page_content

def web_scraper(link):
    try:
        loader = WebBaseLoader(link)
        loader.requests_kwargs = {"verify": False}
        docs = loader.load()
        content = ""
        for doc in docs:
            content += doc.page_content

        return content

    except Exception as e:
        print("Error! : " + str(e))
        return ""


