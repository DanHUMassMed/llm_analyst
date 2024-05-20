""" Methods for searching the internet"""
import os
import json
import urllib.parse
from tavily import TavilyClient
import requests
from duckduckgo_search import DDGS
from llm_analyst.core.exceptions import LLMAnalystsException

def tavily_search(query, max_results=7):
    try:
        api_key = os.environ["TAVILY_API_KEY"]
        client = TavilyClient(api_key)
    except:
        raise Exception("Tavily API key not found. Please set the TAVILY_API_KEY environment variable. "
                        "You can get a key at https://app.tavily.com")

    try:
        # Search the query
        results = client.search(query, search_depth="advanced", max_results=max_results)
        # Return the results
        search_response = [{"href": obj["url"], "body": obj["content"]} for obj in results.get("results", [])]
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"tavily_search Error: {e}")
        search_response = []
        search_response = ddgs_search(query, max_results)
        
    search_response = [obj for obj in search_response if "youtube.com" not in obj["href"]]
    return search_response

def serper_search(query, max_results=7):
    search_response = []
    try:
        api_key = os.environ["SERPER_API_KEY"]
    except:
        raise LLMAnalystsException("SERPER_API_KEY key not found. Please set the SERPER_API_KEY environment variable.")

    try:
        url = "https://google.serper.dev/search"

        headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
        }
        data = json.dumps({"q": query,  "num": max_results})

        resp = requests.request("POST", url, timeout=10, headers=headers, data=data)

        if resp:
            search_results = json.loads(resp.text)
            if search_results:
                results = search_results["organic"]
                for result in results:
                    # skip youtube results
                    if "youtube.com" in result["link"]:
                        continue
                    search_result = {
                        "title": result["title"],
                        "href": result["link"],
                        "body": result["snippet"],
                    }
                    search_response.append(search_result)
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"serper_search Error: {e}")
        
    return search_response

def serp_api_search(query, max_results=7):
    search_response = []
    results_processed = 0
    try:
        api_key = os.environ["SERP_API_KEY"]
    except:
        raise LLMAnalystsException("SERP_API_KEY key not found. Please set the SERP_API_KEY environment variable.")

    url = "https://serpapi.com/search.json"
    params = {
        "q": query,
        "api_key": api_key
    }
    encoded_url = url + "?" + urllib.parse.urlencode(params)

    try:
        response = requests.get(encoded_url, timeout=10)
        if response.status_code == 200:
            search_results = response.json()
            if search_results:
                results = search_results["organic_results"]
                for result in results:
                    # skip youtube results
                    if "youtube.com" in result["link"]:
                        continue
                    if results_processed >= max_results:
                        break
                    search_result = {
                        "title": result["title"],
                        "href": result["link"],
                        "body": result["snippet"],
                    }
                    search_response.append(search_result)
                    results_processed += 1
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"serp_api_search Error: {e}")

    return search_response


def ddgs_search(query, max_results=5):
    search_response = []
    try:
        ddg = DDGS()
        search_response = ddg.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=max_results)
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"ddgs_search Error: {e}")
    
    return search_response

