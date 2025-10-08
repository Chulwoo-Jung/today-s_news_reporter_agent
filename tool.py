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
        response = requests.get(url)
        if response.status_code != 200:
            continue
        feed = feedparser.parse(response.text)

        for entry in feed.entries[:each]:
            all_articles.append({
                "source": source_name,
                "title": getattr(entry, "title", "No title"),
                "url": getattr(entry, "link", "No link"),
                "summary": getattr(entry, "summary", "No summary"),
                "published_date": getattr(entry, "published", "No published date"),
            })
    return all_articles

class GlobalNewsResearchToolInput(BaseModel):
    each:int=10

class GlobalNewsResearchTool(BaseTool):
    name:str="global_news_research_tool"
    description:str="Search the web for the latest global news"
    input_schema:Type[BaseModel]=GlobalNewsResearchToolInput

    def _run(self, each:int=10):
        global_url = {
            "Google_News": "https://news.google.com/rss/search?q=financial+news&hl=en-US&gl=US&ceid=US:en",
            "BBC_News": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "New_York_Times": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",
            "Wall_Street_Journal": "https://feeds.feedburner.com/wsj/business-news",
            "Forbes": "https://www.forbes.com/forbesapi/rss/news/google-apple-amazon-facebook-nvidia-to-join-forces-to-build-ai-platform-for-your-house/"
        }
        return _get_rss(global_url, each=each)


class KoreanNewsResearchToolInput(BaseModel):
    each:int=10

class KoreanNewsResearchTool(BaseTool):
    name:str = "korean_news_research_tool"
    description:str = "Search the web for the latest Korean news"
    input_schema:Type[BaseModel] = KoreanNewsResearchToolInput

    def _run(self, each:int=10):
        korean_url = {
            "Chosun_Ilbo": "https://rss.chosun.com/site/data/rss/rss.xml?scode=sc41",
            "Joongang_Ilbo": "https://rss.joongang.joins.com/joongang/section/news/newsflash.xml",
            "Hankook_Ilbo": "https://rss.hankookilbo.com/section/rss/news.xml",
            "Money_Today": "https://www.mt.co.kr/rss/all.xml",
            "Korea_Herald": "https://www.koreaherald.com/rss/news/articlelist.xml"
        }
        return _get_rss(korean_url, each=each)

class WebSearchToolInput(BaseModel):
    url : str = Field(..., description="The URL to look for.")

class WebSearchTool(BaseTool):
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