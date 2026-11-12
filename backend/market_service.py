import os
import requests
from dotenv import load_dotenv

ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
load_dotenv(ENV_PATH)

SERPSTACK_API_KEY = os.environ.get("SERPSTACK_API_KEY")
SERPSTACK_API_URL = "http://api.serpstack.com/search"

# ==========================================
# Simulated Benchmark Fallback Generators
# (Used when Serpstack API key is missing, invalid, or quota exceeded)
# ==========================================

def get_simulated_competitor_analysis(competitor_name):
    """
    Returns curated simulated benchmark data when real-time search is unavailable.
    Explicitly labeled as simulated fallback data without fake URLs.
    """
    clean_name = competitor_name.strip()
    return {
        "competitor": clean_name,
        "is_fallback": True,
        "source": "Illustrative simulated benchmark",
        "source_type": "simulated",
        "disclaimer": "Simulated Market Benchmark: Live search API key is unconfigured or unavailable. The findings below are simulated industry baseline metrics for demonstration purposes.",
        "findings": [
            {
                "title": f"{clean_name} - Retail Pricing & Catalog Benchmarking",
                "snippet": f"Industry retail benchmarks indicate {clean_name} maintains aggressive promotional cycles with average discounting between 10% and 20% on core retail assortments.",
                "url": None
            },
            {
                "title": f"{clean_name} - Customer Sentiment & Foot Traffic Overview",
                "snippet": f"Simulated retail analytics show high customer loyalty index for {clean_name} with weekend foot traffic concentration and competitive assortment overlap.",
                "url": None
            },
            {
                "title": f"{clean_name} - Promotional Strategy & Seasonal Discounting",
                "snippet": f"Recent seasonal campaigns from {clean_name} emphasize loyalty card rewards, multi-buy discounts, and targeted digital circulars.",
                "url": None
            }
        ],
        "status": "success"
    }, 200

def get_simulated_keyword_search(topic):
    """
    Returns curated simulated keyword search data when real-time search is unavailable.
    Explicitly labeled as simulated fallback data without fake URLs.
    """
    clean_topic = topic.strip()
    return {
        "topic": clean_topic,
        "is_fallback": True,
        "source": "Illustrative simulated benchmark",
        "source_type": "simulated",
        "disclaimer": "Simulated Market Benchmark: Live search API is unconfigured or unavailable. The keyword metrics below are simulated retail search estimates for demonstration purposes.",
        "top_results": [
            {
                "title": f"Demand Trends & Retail Search Volume for {clean_topic}",
                "snippet": f"Simulated retail index highlights growing consumer search interest for {clean_topic}, with regional demand spikes during holiday and promotional periods.",
                "url": None
            },
            {
                "title": f"Pricing Benchmarks & Consumer Demand: {clean_topic}",
                "snippet": f"Competitive category analysis suggests premium price elasticity for top-tier {clean_topic} offerings and margin compression on entry-level alternatives.",
                "url": None
            }
        ],
        "related_keywords": [
            f"{clean_topic} promotional discounts",
            f"{clean_topic} retail price comparison",
            f"best seasonal deals on {clean_topic}",
            f"{clean_topic} consumer demand trends",
            f"{clean_topic} store availability"
        ],
        "status": "success"
    }, 200

def get_simulated_trend_discovery(industry):
    """
    Returns curated simulated industry trend data when real-time search is unavailable.
    Explicitly labeled as simulated fallback data without fake URLs.
    """
    clean_ind = industry.strip()
    return {
        "industry": clean_ind,
        "is_fallback": True,
        "source": "Illustrative simulated benchmark",
        "source_type": "simulated",
        "disclaimer": "Simulated Market Benchmark: Live search API is unconfigured or unavailable. The trend findings below are simulated industry insights for demonstration purposes.",
        "recent_trends": [
            {
                "title": f"Macro Trend: Omnichannel Retail Integration in {clean_ind}",
                "snippet": f"Retailers in the {clean_ind} sector are accelerating automated stock replenishment and click-and-collect fulfillment to optimize foot traffic.",
                "url": None
            },
            {
                "title": f"Dynamic Pricing & Promotional Analytics Adoption in {clean_ind}",
                "snippet": f"Adoption of predictive sales modeling and dynamic price elasticity tools is driving margin improvements across {clean_ind} retail leaders.",
                "url": None
            },
            {
                "title": f"Private-Label Expansion vs National Brands in {clean_ind}",
                "snippet": f"Consumer shift toward high-margin private label alternatives in {clean_ind} continues to pressure national brand market share.",
                "url": None
            }
        ],
        "status": "success"
    }, 200

# ==========================================
# Real-Time Search API Wrapper
# ==========================================

def perform_search(query):
    """Base function to perform a web search via Serpstack."""
    ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../.env'))
    load_dotenv(ENV_PATH)
    api_key = os.environ.get("SERPSTACK_API_KEY")
    if not api_key or api_key.strip() in ["your_api_key_here", "your_serpstack_api_key_here", ""]:
        return {"error": "Serpstack API key is missing or invalid. Please configure the .env file.", "status": 500}
    
    params = {
        "access_key": api_key.strip(),
        "query": query,
        "num": 5
    }
    
    try:
        response = requests.get(SERPSTACK_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                 return {"error": data["error"].get("info", "Unknown API error"), "status": 500}
            return {"data": data, "status": 200}
        else:
            return {"error": f"Search API failed with status code {response.status_code}", "status": response.status_code}
            
    except requests.exceptions.Timeout:
        return {"error": "Search API request timed out.", "status": 504}
    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred during search: {str(e)}", "status": 500}

def get_competitor_analysis(competitor_name):
    """Retrieves search data for competitor analysis, with graceful simulated fallback."""
    query = f"{competitor_name} pricing reviews products"
    result = perform_search(query)
    
    if result.get("status") == 200 and "data" in result:
        organic_results = result["data"].get("organic_results", [])
        extracted_info = [
            {"title": res.get("title"), "snippet": res.get("snippet"), "url": res.get("url")}
            for res in organic_results
        ]
        return {
            "competitor": competitor_name,
            "findings": extracted_info,
            "is_fallback": False,
            "source": "Live Serpstack Search",
            "source_type": "live",
            "disclaimer": None,
            "status": "success"
        }, 200
    
    # Graceful fallback when search API fails or is unconfigured
    return get_simulated_competitor_analysis(competitor_name)

def get_keyword_search(topic):
    """Retrieves search data for keyword and market research, with graceful simulated fallback."""
    query = f"{topic} market trends demand"
    result = perform_search(query)
    
    if result.get("status") == 200 and "data" in result:
        organic_results = result["data"].get("organic_results", [])
        related_searches = result["data"].get("related_searches", [])
        
        extracted_info = [
            {"title": res.get("title"), "snippet": res.get("snippet"), "url": res.get("url")}
            for res in organic_results
        ]
        
        keywords = [rs.get("query") for rs in related_searches] if related_searches else []
        
        return {
            "topic": topic,
            "top_results": extracted_info,
            "related_keywords": keywords,
            "is_fallback": False,
            "source": "Live Serpstack Search",
            "source_type": "live",
            "disclaimer": None,
            "status": "success"
        }, 200
        
    # Graceful fallback when search API fails or is unconfigured
    return get_simulated_keyword_search(topic)

def get_trend_discovery(industry):
    """Retrieves search data for recent industry trends, with graceful simulated fallback."""
    query = f"{industry} recent trends news"
    result = perform_search(query)
    
    if result.get("status") == 200 and "data" in result:
        organic_results = result["data"].get("organic_results", [])
        extracted_info = [
            {"title": res.get("title"), "snippet": res.get("snippet"), "url": res.get("url")}
            for res in organic_results
        ]
        return {
            "industry": industry,
            "recent_trends": extracted_info,
            "is_fallback": False,
            "source": "Live Serpstack Search",
            "source_type": "live",
            "disclaimer": None,
            "status": "success"
        }, 200
        
    # Graceful fallback when search API fails or is unconfigured
    return get_simulated_trend_discovery(industry)
