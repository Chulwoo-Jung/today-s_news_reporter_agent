import os
from dotenv import load_dotenv
from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
from datetime import datetime
from tool import web_search_tool, global_news_research_tool, korean_news_research_tool

load_dotenv()

FETCH_NEWS_COUNT = 10

class NewsCrew:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")

    def research_specialist_agent(self) -> Agent:
        return Agent(
            role="Research Specialist",
            goal="Collect as many latest news articles from RSS feeds as possible",
            backstory="""
            You are a veteran research specialist with 20 years of experience at a global news agency.
            You are an expert at thoroughly searching various sources (Google News RSS, major domestic and international media outlets)
            to find highly relevant and latest trending news articles.
            You collect news updated in real-time through RSS feeds and
            filter out duplicates to select only the most valuable information.
            """,
            llm=self.llm,
            verbose=True,
            tools=[global_news_research_tool, korean_news_research_tool],
        )

    def research_global_news_task(self) -> Task:
        return Task(
            agent=self.research_specialist_agent(),
            description=f"""
            Today is {datetime.now().strftime("%Y-%m-%d")}
            Collect the latest news articles from global news RSS sources.

            **Required Steps (Must Follow):**

            1. **First, call global_news_research_tool** to fetch actual RSS data.
            2. **Wait for the tool result and use only the actual data received**.
            3. **Never generate arbitrary news or example data.**
            4. Sort the data received from the RSS tool by importance and relevance (prioritize latest).
            5. Remove duplicate articles.
            6. Select the top {FETCH_NEWS_COUNT} hottest news articles.

            **Warning: This task is for actual news collection, so you must call global_news_research_tool.
            Creating fake news from previous dates is strictly prohibited.
            The RSS tool provides current real news.**
            """,
            expected_output=f"""
            JSON list in the following format:
            [
                {{
                    "title": "Article title",
                    "url": "Article URL",
                    "summary": "Article summary",
                    "published_date": "Publication date",
                    "source": "News source",
                    "category": "Category",
                    "importance_score": "Importance score 1-10"
                }}
            ]
            Maximum {FETCH_NEWS_COUNT} global news articles
            """,
            output_file="output/global_news.json",
            tools=[global_news_research_tool]
        )

    def research_korean_news_task(self) -> Task:
        return Task(
            agent=self.research_specialist_agent(),
            description=f"""
            Today is {datetime.now().strftime("%Y-%m-%d")}
            Collect the latest news articles from major Korean media RSS feeds.

            **Required Steps (Must Follow):**

            1. **First, call korean_news_research_tool** to fetch actual RSS data.
            2. **Wait for the tool result and use only the actual data received**.
            3. **Never generate arbitrary news or example data.**
            4. Analyze the data received from the RSS tool by importance and timeliness.
            5. Remove duplicate and similar articles.
            6. Select the top {FETCH_NEWS_COUNT} hottest Korean news.

            **Warning: This task is for actual news collection, so you must call korean_news_research_tool.
            Creating fake news from previous dates is strictly prohibited.
            The RSS tool provides current real news.**
            """,
            expected_output=f"""
            JSON list in the following format:
            [
                {{
                    "title": "Article title",
                    "url": "Article URL",
                    "summary": "Article summary",
                    "published_date": "Publication date",
                    "source": "Media outlet name",
                    "category": "Category (Politics/Economy/Society/International etc.)",
                    "importance_score": "Importance score 1-10"
                }}
            ]
            Maximum {FETCH_NEWS_COUNT} Korean news articles
            """,
            output_file="output/korean_news.json",
            tools=[korean_news_research_tool]
        )

    def editor_agent(self) -> Agent:
        return Agent(
            role="Senior Editor",
            goal="Extract the actual content of collected news articles and summarize key points in a consistent format.",
            backstory="""
            You are a veteran editor with 15 years of experience at major domestic and international media outlets.
            You are an expert at analyzing news articles in various languages and extracting key content.
            You accurately identify the main text of web articles, filter out advertisements and unnecessary content,
            and have the ability to summarize in an easy-to-understand way for readers.
            You naturally translate English articles into Korean and
            organize all articles in a consistent format.
            """,
            llm=self.llm,
            verbose=True,
            tools=[web_search_tool],
        )

    def edit_and_summarize_articles_task(self) -> Task:
        return Task(
            agent=self.editor_agent(),
            description="""
            Extract the actual article content and summarize the global and Korean news articles collected by the research agent.

            **Required Steps:**

            1. **Use Previous Task Results**:
               - Use all news article data collected from research_global_news_task and research_korean_news_task.
               - Access the URL in the link field of each article to extract the actual article content.

            2. **Extract Article Content**:
               - Access each news link to extract the actual article content.
               - Exclude unnecessary content such as advertisements, related articles, and comments, and extract only the core article content.
               - Clearly separate title, date, content, and source.

            3. **Summarize and Translate Content**:
               - Naturally translate English articles into Korean.
               - Summarize the key content of each article in 2-3 sentences.
               - Organize clearly and concisely without distorting the original meaning.

            4. **Process All Articles**:
               - Perform work on all collected articles (process all, not just selected ones).
               - Process each article with the same quality.
               - Skip inaccessible links and process only accessible articles.

            **Important Guidelines:**
            - You must access the actual website to get the article content.
            - Don't rely on existing RSS summaries, read and summarize the entire article.
            - Translate all foreign language articles into Korean.
            - Process all articles in a consistent format.
            """,
            expected_output="""
            JSON list in the following format:
            [
                {
                    "original_title": "Original article title",
                    "title": "Translated article title (in Korean)",
                    "published_date": "Publication date",
                    "source": "Source",
                    "category": "Category (Politics/Economy/Society/International/Sports/Culture etc.)",
                    "original_summary": "Original RSS summary",
                    "full_content_summary": "Detailed summary based on actual article content (in Korean, 2-3 sentences)",
                    "key_points": ["Key point 1", "Key point 2", "Key point 3"],
                    "article_url": "Original article URL",
                    "importance_score": "Importance score 1-10"
                }
            ]
            Detailed analysis results of all global and Korean news articles
            """,
            output_file="output/news_summary.json"
        )

    def curator_agent(self) -> Agent:
        return Agent(
            role="News Curator",
            goal="Select the 10 most important and relevant news articles from edited news and write a final report.",
            backstory="""
            You are Korea's top news curation expert with over 10 years of experience.
            You comprehensively analyze news from various fields and have the ability to select the most important information that readers need to know.
            You balance global and domestic news while considering timeliness and importance
            to carefully select only the most valuable news for readers.
            Finally, you write a well-formatted report so that readers can easily understand.
            """,
            llm=self.llm,
            verbose=True,
            tools=[]
        )

    def curate_final_news_task(self) -> Task:
        return Task(
            agent=self.curator_agent(),
            description=f"""
            Today is {datetime.now().strftime("%Y-%m-%d")}
            Analyze all edited news articles and select the 10 most important and relevant news to write a final report.

            **Required Steps:**

            1. **Use Previous Task Results**:
               - Analyze all edited article data generated from edit_and_summarize_articles_task.
               - Comprehensively evaluate the importance score, category, and content of each article.

            2. **News Selection Criteria**:
               - Prioritize articles with good importance scores (7 or above preferred)
               - Limit global news to about 30% (3 articles) of the total
               - Compose Korean news to about 70% (7 articles) of the total
               - Balance various categories (Politics/Economy/Society/International etc.)
               - Consider timeliness and social impact

            3. **Write Final Report**:
               - Organize the selected 10 articles in a visually appealing manner
               - Clearly display headline, summary, original source, and source for each article
               - Add a brief summary of overall news trends
               - Compose in an easy-to-understand format for readers

            **Selection Priority:**
            1. Importance score (7 or above)
            2. Timeliness (recency)
            3. Social impact
            4. Category diversity
            5. Global/Domestic news ratio (3:7)
            """,
            expected_output="""
            Final news report in TXT format:

            ============================================
                        Today's Major News Report
                        [Date: YYYY-MM-DD]
            ============================================

            📊 **News Briefing Summary**
            - Global News: 3 articles (30%)
            - Domestic News: 7 articles (70%)
            - Major Issues: [Overall trend summary]

            ============================================
                            📰 Major News
            ============================================

            [1] 🌍 [Category] Headline
            📅 Published: YYYY-MM-DD
            📰 Source: Media outlet name
            🔗 Original: URL

            📝 Summary:
            [Key content summary in 2-3 sentences]

            💡 Key Points:
            • Key point 1
            • Key point 2
            • Key point 3

            ────────────────────────────────────────

            [Repeat...]

            ============================================
                        📋 Overall News Trend Analysis
            ============================================

            **Today's Major Issues:**
            [Overall trend analysis and summary based on 10 selected news]

            **Distribution by Category:**
            - Politics: X articles
            - Economy: X articles
            - Society: X articles
            - International: X articles
            - Others: X articles

            **Notable Trends:**
            [Overall news trends and pattern analysis]

            ============================================
            """,
            output_file="output/final_news_briefing.md",
            context=[self.edit_and_summarize_articles_task()]
        )

    def crew(self) -> Crew:
        return Crew(
            agents=[self.research_specialist_agent(), self.editor_agent(), self.curator_agent()],
            tasks=[self.research_global_news_task(), self.research_korean_news_task(), self.edit_and_summarize_articles_task(), self.curate_final_news_task()],
            verbose=True
        )

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    NewsCrew().crew().kickoff()
