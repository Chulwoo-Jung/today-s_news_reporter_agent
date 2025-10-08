from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from firecrawl import Firecrawl
import feedparser
import requests
from env import FIRECRAWL_API_KEY
from typing import Type, Any

def _get_rss(rss_url:dict[str,str], each:int=10):
    all_articles = []
    for source_name, url in rss_url.items():
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for bad status codes
            feed = feedparser.parse(response.text)

            for entry in feed.entries[:each]:
                all_articles.append({
                    "source": source_name,
                    "title": getattr(entry, "title", "No title"),
                    "url": getattr(entry, "link", "No link"),
                    "summary": getattr(entry, "summary", "No summary"),
                    "published_date": getattr(entry, "published", "No published date"),
                    "category": getattr(entry, "category", "General"),  # Added missing category field
                    "importance_score": 0  # Added missing importance_score field
                })
        except Exception as e:
            print(f"Error fetching RSS from {source_name}: {str(e)}")
            continue
    return all_articles

class GlobalNewsResearchToolInput(BaseModel):
    each: int = Field(default=10, description="Number of articles to fetch per source")

class GlobalNewsResearchTool(BaseTool):
    name: str = "global_news_research_tool"
    description: str = "Search the web for the latest global news"
    input_schema: Type[BaseModel] = GlobalNewsResearchToolInput

    def _run(self, each: int = 10) -> list[dict]:
        global_url = {
            "Google News": "https://news.google.com/rss/search?q=global+economy+finance&hl=en-US&gl=US&ceid=US:en",
            "BBC": "https://feeds.bbci.co.uk/news/business/rss.xml",
            "CNN": "https://rss.cnn.com/rss/money_news_international.rss",
        }
        return _get_rss(global_url, each=each)

class KoreanNewsResearchToolInput(BaseModel):
    each: int = Field(default=10, description="Number of articles to fetch per source")

class KoreanNewsResearchTool(BaseTool):
    name: str = "korean_news_research_tool"
    description: str = "Search the web for the latest Korean news"
    input_schema: Type[BaseModel] = KoreanNewsResearchToolInput

    def _run(self, each: int = 10) -> list[dict]:
        korean_rss_feeds = {
            "연합뉴스": "https://www.yna.co.kr/RSS/economy.xml",  # Changed to economy feed
            "조선일보": "https://www.chosun.com/arc/outboundfeeds/rss/economy/?outputType=xml",
            "동아일보": "https://rss.donga.com/economy.xml",
            "매일경제": "https://www.mk.co.kr/rss/30000001/",
            "한국경제": "https://www.hankyung.com/feed/economy",
        }
        return _get_rss(korean_rss_feeds, each=each)

class WebSearchToolInput(BaseModel):
    url: str = Field(..., description="The URL to look for.")

class WebSearchTool(BaseTool):
    name: str = "web_search_tool"
    description: str = "Web Content Scraper Tool. Scrape the web for the information based on the URL. Return the result in text format."
    input_schema: Type[BaseModel] = WebSearchToolInput
    
    def _run(self, url: str) -> dict[str, str]:
        try:
            app = Firecrawl(api_key=FIRECRAWL_API_KEY)
            response: Any = app.scrape(url=url)

            title = getattr(response, "title", "No Title")
            content = "No Content"
            
            if hasattr(response, "content"):
                content = response.content
            elif hasattr(response, "metadata"):
                content = response.metadata
            elif hasattr(response, "markdown"):
                content = response.markdown
            
            return {
                "title": title,
                "url": url,
                "content": content
            }
        except Exception as e:
            print(f"Error scraping URL {url}: {str(e)}")
            return {
                "title": "Error",
                "url": url,
                "content": f"Failed to scrape content: {str(e)}"
            }

    name:str = "web_search_tool"
    description:str = "Web Content Scraper Tool. Scrape the web for the information based on the URL. Return the result in text format."
    input_schema:Type[BaseModel] = WebSearchToolInput
    
    def _run(self, url:str) -> dict[str, str]:
        app = Firecrawl(api_key=FIRECRAWL_API_KEY)
        response : Any = app.scrape(url=url)

        title = "No Title"
        if hasattr(response, "title"):
            title = response.title
        
        content = "No Content"
        if hasattr(response, "content"):
            content = response.content
        elif hasattr(response, "metadata"):
            content = response.metadata
        elif hasattr(response, "markdown"):
            content = response.markdown
        
        result = {
            "title": title,
            "url": url,
            "content": content
        }
        return result

web_search_tool = WebSearchTool()
global_news_research_tool = GlobalNewsResearchTool()
korean_news_research_tool = KoreanNewsResearchTool()