""" Methods for searching the internet"""
import os
import json
import urllib.parse
from tavily import TavilyClient
import requests
from duckduckgo_search import DDGS
from llm_analyst.core.exceptions import LLMAnalystsException

def tavily_search(query, max_results=7):
    """Tavily is a search engine built specifically for AI agents (LLMs).
       As of May 2024 Tavily has Free tier allows 1,000 Free searches per month
       https://tavily.com/
    """
    try:
        api_key = os.environ["TAVILY_API_KEY"]
        client = TavilyClient(api_key)
    except:
        raise LLMAnalystsException("Tavily API key not found. Please set the TAVILY_API_KEY environment variable. "
                        "You can get a key at https://app.tavily.com")

    try:
        # Search the query
        results = client.search(query, search_depth="advanced", max_results=max_results)
        # Return the results
        search_response = [{"href": obj["url"], "body": obj["content"]} for obj in results.get("results", [])]
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"tavily_search Error: {e}")
        search_response = ddg_search(query, max_results)
        
    search_response = [obj for obj in search_response if "youtube.com" not in obj["href"]]
    return search_response

def serper_search(query, max_results=7):
    """Fast and Cheap Google Search API
       As of May 2024 Serper has no Free tier
       but does allow 2,500 Free searches before you must pay"""
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
    except Exception as e: 
        print(f"serper_search Error: {e}")
        search_response = ddg_search(query, max_results)

        
    return search_response

def serp_api_search(query, max_results=7):
    """Scrape Google and other search engines from our fast, easy, and complete API.
       As of May 2024 SerpAPI Free tier allows 100 searches / month
       https://serpapi.com
    """
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
    except Exception as e:
        print(f"serp_api_search Error: {e}")
        search_response = ddg_search(query, max_results)

    return search_response


def ddg_search(query, max_results=5):
    """DuckDuckGo is a free private search engine.
       As of May 2024 DuckDuckGo is Free not search limits
       https://duckduckgo.com/"""
    search_response = []
    try:
        ddg = DDGS()
        search_response = ddg.text(query, region='wt-wt', safesearch='off', timelimit='y', max_results=max_results)
    except Exception as e: # Fallback in case overload on Tavily Search API
        print(f"ddgs_search Error: {e}")
    
    return search_response


def google_search(query, max_results=7):
    """Google Search no explaination needed
       As of May 2024 Google has Free tier allows 100 Free searches per day
       https://developers.google.com/custom-search/v1/overview
    """
    search_response = []
    results_processed = 0
    
    try:
        api_key = os.environ["GOOGLE_API_KEY"]
    except:
        raise Exception("Google API key not found. Please set the GOOGLE_API_KEY environment variable. "
                        "You can get a key at https://developers.google.com/custom-search/v1/overview")

    try:
        cx_key = os.environ["GOOGLE_CX_KEY"]
    except:
        raise Exception("Google CX key not found. Please set the GOOGLE_CX_KEY environment variable. "
                        "You can get a key at https://developers.google.com/custom-search/v1/overview")

    try:
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cx_key,
            "q": query,
            "start": 1
        }
        encoded_url = url + "?" + urllib.parse.urlencode(params)

        response = requests.get(encoded_url, timeout=10)

        if response is None:
            return search_response
        try:
            search_results_json = json.loads(response.text)
        except Exception:
            return search_response
        if search_results_json is None:
            return search_response

        results = search_results_json.get("items", [])
        
        # Normalizing results to match the format of the other search APIs
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

    except Exception as e: 
        print(f"tavily_search Error: {e}")
        search_response = ddg_search(query, max_results)
        
    
    return search_response

def bing_search(query, max_results=7):
    search_response = []
    try:
        api_key = os.environ["BING_API_KEY"]
    except:
        raise Exception("Bing API key not found. Please set the BING_API_KEY environment variable.")
    
        # Search the query
    url = "https://api.bing.microsoft.com/v7.0/search"

    headers = {
    'Ocp-Apim-Subscription-Key': api_key,
    'Content-Type': 'application/json'
    }
    params = {
        "responseFilter" : "Webpages",
        "q": query,
        "count": max_results,
        "setLang": "en-GB",
        "textDecorations": False,
        "textFormat": "HTML",
        "safeSearch": "Strict"
    }
    
    resp = requests.get(url, headers=headers, params=params, timeout=10)

    # Preprocess the results
    if resp is None:
        return search_response
    try:
        search_results = json.loads(resp.text)
    except Exception:
        return search_response
    if search_results is None:
        return search_response

    results = search_results["webPages"]["value"]
    

    # Normalize the results to match the format of the other search APIs
    for result in results:
        # skip youtube results
        if "youtube.com" in result["url"]:
            continue
        search_result = {
            "title": result["name"],
            "href": result["url"],
            "body": result["snippet"],
        }
        search_response.append(search_result)

    return search_response

