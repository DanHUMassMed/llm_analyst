"""
This module provides various scraping functions to extract content from different types of web links.
It includes specialized scrapers for arXiv links, PDF files, generic web pages, and pages requiring
Selenium for dynamic content loading. The main function `scrape_urls` determines the appropriate 
scraper based on the URL and aggregates the content into a list of strings.
"""

import importlib
import os
import re
import uuid
from concurrent.futures.thread import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.document_loaders.pdf import PyMuPDFLoader
from langchain_community.document_loaders.web_base import WebBaseLoader
from langchain_community.retrievers.arxiv import ArxivRetriever
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def arxiv_scraper(link):
    query = link.split("/")[-1]
    retriever = ArxivRetriever(load_max_docs=2, doc_content_chars_max=None)
    docs = retriever.invoke(query)
    # Just pulling the abstract
    return docs[0].page_content


def pdf_scraper(link):
    loader = PyMuPDFLoader(link)
    docs = loader.load()
    content = ""
    for doc in docs:
        content += doc.page_content
    return content


def bs_scraper(link):
    """
    This is a Beautiful Soup Scraper however web_scraper also uses Beautiful Soup
    and does so more seamlessly.
    """
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


def cell_selenium_scraper(link):
    """
    Works as a general site scraper however this was implemented specifically 
    to scrape cell.com sites.
    """
    display = Display(visible=0, size=(800, 600))
    display.start()

    # Set up the browser
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    browser = webdriver.Firefox(options=options)
    browser.get(link)

    try:
        # Wait for the cookie consent button to be present and clickable
        cookie_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
        )
        # Click the cookie consent button
        cookie_button.click()
    except Exception as e:
        print("No cookie consent button found or an error occurred:", e)

    # Get the whole web page content
    page_source = browser.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    # Extract text content and print it
    text_content = soup.get_text()
    pattern = r"\s{3,}"
    text_content = re.sub(pattern, "  ", text_content)
            
    # Clean up
    browser.quit()
    display.stop()

    return text_content



def web_scraper(link):
    try:
        loader = WebBaseLoader(link)
        loader.requests_kwargs = {"verify": False}
        docs = loader.load()
        content = ""
        for doc in docs:
            content += doc.page_content

        pattern = r"\s{3,}"
        content = re.sub(pattern, "  ", content)
        return content

    except Exception as e:
        print("Error! : " + str(e))
        return ""

#################################################################################

def scrape_urls(urls):
    """
    Given a list of URLs
    1. Determine an appropriate scraper based on URL content
    2. For each URL Scrape the website and aggregate the content into a list of strings
        one for each site
    """

    def extract_data_from_link(link):
        if link.endswith(".pdf"):
            scraper_nm = "pdf_scraper"
        elif "arxiv.org" in link:
            scraper_nm = "arxiv_scraper"
        elif "cell.com" in link:
            scraper_nm = "cell_selenium_scraper"
        else:
            #scraper_nm = "bs_scraper"
            scraper_nm = "web_scraper"

        content = ""
        try:
            module_nm = "llm_analyst.scrapers.scraper_methods"
            module = importlib.import_module(module_nm)
            scrape_content = getattr(module, scraper_nm)
            content = scrape_content(link)

            if len(content) < 100:
                return {"url": link, "raw_content": None}
            return {"url": link, "raw_content": content}
        except Exception:
            return {"url": link, "raw_content": None}

    content_list = []
    try:
        with ThreadPoolExecutor(max_workers=20) as executor:
            contents = executor.map(extract_data_from_link, urls)
        content_list = [
            content for content in contents if content["raw_content"] is not None
        ]

    except Exception as e:
        print(f"Error in scrape_urls: {e}")
    return content_list
