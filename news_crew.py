import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from datetime import datetime
from tool import web_search_tool, global_news_research_tool, korean_news_research_tool

load_dotenv()

class NewsCrew:
    def __init__(self, global_news_account:int=10, korean_news_account:int=10):
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.global_news_account = global_news_account
        self.korean_news_account = korean_news_account

    def research_agent(self) -> Agent:
        return Agent(
            role="Research Specialist",
            goal="Research the latest economic and financal news in RSS format as much as possible.",
            backstory="""
            You are a research specialist for 20 years with a strong background in economics and finance.
            You are particularly a expert in researching latest and 'must-know' global economic and financial news from diverse news agencies.
            Collect the live updated news in RSS format as much as possible and get rid of the irrelevant and redundant news.
            Focus on the news that are related to the economic and financial news that are critical and impactful.
            """,
            verbose=True,
            llm=self.llm,
            tools=[]
        )
    
    def research_global_news(self) -> Task:
        return Task(
            agent= self.research_agent(),
            description=f""" 
            Today is {datetime.now().strftime("%Y-%m-%d")}
            Research the latest economic and financial news in *RSS format* as much as possible.
            *** Working Instructions, please follow them strictly ***
            1. Call the 'global_news_research_tool' to research the latest economic and financial news in RSS format.
            2. Use only the result from the 'global_news_research_tool' to generate the RSS feed. Don't use any other information.
            3. Order the news by the importance and relevance to the economic and financial news.
            4. Remove the news that are irrelevant and redundant.
            5. Extract {self.global_news_account} news, that are 'must-know' news, and include the critical information.
            ** Important **
            - This task must use the 'global_news_research_tool' to research the latest economic and financial news in RSS format.
            - Keep in mind the date of today.
            - Don't hallucinate or make up any fake information.
            """,
            expected_output="""
            List of JSON format 
            [
                {
                    "title": "Title of the news",
                    "url": "URL of the news",
                    "category": "Category of the news",
                    "summary": "Summary of the news",
                    "published_date": "Published date of the news",
                    "source": "Source of the news",
                    "importance_score": "Importance score of the news",
                },
                ...
            ]
            maximum {self.global_news_account} news.
            """,
            output_file="output/global_news.json",
            tools=[global_news_research_tool]
        )
    

    def research_korean_news(self) -> Task:
        return Task(
            agent= self.research_agent(),
            description=f"""
            Today is {datetime.now().strftime("%Y-%m-%d")}
            Research the latest Korean economic and financial news in *RSS format* as much as possible.
            *** Working Instructions, please follow them strictly ***
            1. Call the 'korean_news_research_tool' to research the latest Korean economic and financial news in RSS format.
            2. Use only the result from the 'korean_news_research_tool' to generate the RSS feed. Don't use any other information.
            3. Order the news by the importance and relevance to the Korean economic and financial news.
            4. Remove the news that are irrelevant and redundant.
            5. Extract {self.korean_news_account} news, that are 'must-know' news, and include the critical information.
            ** Important **
            - This task must use the 'korean_news_research_tool' to research the latest Korean economic and financial news in RSS format.
            - Keep in mind the date of today.
            - Don't hallucinate or make up any fake information.
            """,
            expected_output="""
            List of JSON format 
            [
                {
                    "title": "Title of the news",
                    "url": "URL of the news",
                    "category": "Category of the news",
                    "summary": "Summary of the news",
                    "published_date": "Published date of the news",
                    "source": "Source of the news",
                    "importance_score": "Importance score of the news",
                },
                ...
            ]
            maximum {self.korean_news_account} news.
            """,
            output_file="output/korean_news.json",
            tools=[korean_news_research_tool]
        )

    def editor_agent(self) -> Agent:
        return Agent(
            role="Professional Senior Editor",
            goal=""" 
            Extract the news content and summarize the relevant and important content. 
            Finally, process the summary to make it more readable and engaging in the same format consistently.",
            """,
            backstory="""
            You are a editor for 20 years with a strong background in economics and finance.
            You can analyze the news content and summarize perfectly in diverse languages.
            You are particularly able to figure out the critical and important content in the news and get rid of the irrelevant and redundant content.
            You are able to process the summary to make it more readable and engaging in the same format consistently.
            Order the news summary in the same format consistently.
            """,
            verbose=True,
            llm=self.llm,
            tools=[web_search_tool]
        )

    def edit_and_summarize_news(self) -> Task:
        return Task(
            agent  = self.editor_agent(),
            description="""
            Extract the critical and important news content and summarize the relevant and important content.
            *** Working Instructions, please follow them strictly ***
            1. Utilize the previous research result of tasks
                - Use all the research result from research_global_news and research_korean_news tasks.
                - Access the URL for each news and extract the whole content from the site.
            2. Extract the whole content from the site
                - Access the URL for each news and extract the whole content from the site.
                - Extract the critical and important news content without commercial advertisement and irrelevant content.
                - Clarify the title, published date, content, and source of the news.
            3. Translate the content into English 
                - Translate the content into English if it is not in English.
            4. Summarize the relevant and important content.
                - Summarize the critical and important news content in the same format consistently.
                - Summarized the content in 4-5 sentences.
                - Keep the original point of news and the core message of the news.
            ** Important **
            - Access the real URL from the research result of previous tasks.
            - Don't rely on the summary in RSS format, read the whole content from the site.
            - Process all the newses in the same way and summarize them in the same format consistently.
            - Don't hallucinate or make up any fake information.
            """,
            expected_output="""
            List of JSON format 
            [
                {
                    "original_title": "Original title of the news",
                    "url": "URL of the news",
                    "source": "Source of the news",
                    "published_date": "Published date of the news",
                    "category": "Category of the news",
                    "original_summary": "Original summary of the news in RSS format",
                    "full_content_summary": "Summary of the news",
                },
                ...
            ]
            """,
            output_file="output/news_summary.json"
        )

    def curator_agent(self) -> Agent:
        return Agent(
            role="Professional News Curator",
            goal="Clarify the 10 most important news and write the final news report.",
            backstory="""
            You are a curator for 20 years with a strong background in economics and finance.
            You can analyse the news economics and financial news and, clarify the most important 10 news, what readers must know.
            Balance between the global and Korean news, while considering the importance and critical economic and financial situation.
            Write the final news report in the same format consistently.
            """,
            verbose=True,
            llm=self.llm,
            tools=[]
        )

    def curate_final_news_task(self) -> Task:
        return Task(
            agent = self.curator_agent(),
            description=f"""
            Today is {datetime.now().strftime("%Y-%m-%d")}
            Curate and select the 10 most important news from the previous research and summarization results.
            *** Working Instructions, please follow them strictly ***
            1. Utilize all the previous task results
                - Use all the summarized news content from the edit_and_summarize_news task.
                - Analyze each news article's importance, relevance, and impact on the economy and finance.
            2. Select the top 10 most important news
                - Balance between global and Korean news (aim for approximately 5-6 global news and 4-5 Korean news).
                - Consider the following criteria for selection:
                    * Economic impact: How significantly does this news affect the economy?
                    * Timeliness: How recent and relevant is this news?
                    * Scope: Does it affect individuals, corporations, or entire countries?
                    * Urgency: Is this something readers must know immediately?
                    * Long-term implications: Will this have lasting effects?
            3. Rank the selected news by importance
                - Rank from 1 to 10, with 1 being the most important.
                - Provide a brief justification for why each news is important.
            4. Write a professional news briefing
                - Create an executive summary (2-3 sentences) highlighting the key themes of the day.
                - For each news item, provide a clear and engaging title, summary, and key takeaways.
                - Maintain a professional yet accessible tone.
            ** Important **
            - Use only the information from previous tasks. Don't add external information.
            - Ensure balance between global and Korean news.
            - Focus on economic and financial significance.
            - Don't hallucinate or make up any fake information.
            - Keep the format consistent and professional.
            """,
            expected_output="""
            A professional news briefing report in Markdown format with the following structure:
            
            # Daily Economic & Financial News Briefing
            **Date:** YYYY-MM-DD
            
            ## Executive Summary
            2-3 sentences highlighting the key economic and financial themes of the day.
            
            ---
            
            ## Top 10 News of the Day
            
            ### 1. [Clear and engaging title]
            **Source:** Source name | **Published:** YYYY-MM-DD | **Category:** Category | **Region:** Global/Korean
            
            **Summary:**
            3-4 sentence summary of the news providing key information and context.
            
            **Key Takeaways:**
            - Key point 1
            - Key point 2
            - Key point 3
            
            **Why This Matters:**
            1-2 sentences explaining the importance and impact of this news.
            
            **Read More:** [Original Article](URL)
            
            ---
            
            ### 2. [Clear and engaging title]
            ... (repeat the same format for all 10 news items)
            
            ---
            
            ## Summary Statistics
            - **Total News Covered:** 10
            - **Global News:** 5-6 articles
            - **Korean News:** 4-5 articles
            
            ---
            
            *Report generated by AI News Curator*
            """,
            output_file="output/final_news_briefing.md",
            context=[self.edit_and_summarize_news()]
        )
    
    def crew(self) -> Crew:
        return Crew(
            agents=[self.research_agent(), self.editor_agent(), self.curator_agent()],
            tasks = [self.research_global_news(), self.research_korean_news(), self.edit_and_summarize_news(), self.curate_final_news_task()],
            verbose=True
        )

if __name__ == "__main__":
    # output 디렉토리 생성
    os.makedirs("output", exist_ok=True)
    
    # Crew 실행
    NewsCrew().crew().kickoff()