# 📰 AI News Briefing Bot

An intelligent news aggregation and delivery system that combines **CrewAI multi-agent framework** with **Telegram Bot** to provide personalized daily news briefings.

## 🎯 Project Overview

This project demonstrates a production-ready AI agent system that:
- **Collects** latest economic and financial news from multiple RSS feeds (Global + Korean sources)
- **Analyzes** and summarizes articles using AI agents with specialized roles
- **Curates** the top 10 most important news stories based on relevance and impact
- **Delivers** personalized news briefings via Telegram on-demand or on schedule

The system leverages a **multi-agent architecture** where specialized AI agents collaborate to research, edit, and curate news content, mimicking a real newsroom workflow.

---

## 📚 Tech Stack & Libraries

Based on `pyproject.toml`, this project uses the following key libraries:

### **Core Framework**
- **`crewai[tools] >= 0.22.0`** - Multi-agent orchestration framework for collaborative AI workflows
- **`langchain >= 0.3.27`** - LLM application framework
- **`langchain-openai >= 0.3.35`** - OpenAI integration for LangChain

### **News Collection & Processing**
- **`feedparser >= 6.0.11`** - RSS/Atom feed parser for collecting news from multiple sources
- **`firecrawl-py >= 3.4.0`** - Web scraping tool for extracting full article content

### **Bot & Scheduling**
- **`python-telegram-bot[job-queue] >= 22.3`** - Telegram bot framework with job scheduling capabilities
- **`pytz >= 2025.2`** - Timezone handling for scheduled news delivery

### **Utilities**
- **`dotenv >= 0.9.9`** - Environment variable management for API keys and configuration

---

## 🤖 CrewAI Architecture Design

### **System Overview**

The news briefing system is built using CrewAI's multi-agent framework with **3 specialized agents** collaborating through **4 sequential tasks**. Each agent has a distinct role, mimicking a real newsroom organization.

### **🔧 Tools (`tool.py`)**

Three custom tools power the information gathering process:

#### **1. GlobalNewsResearchTool**
```python
Purpose: Fetch global economic/financial news from RSS feeds
Sources: Google News, BBC Business, CNN Money
Output: List of articles with {title, url, summary, published_date, source, category, importance_score}
Parameters: No input required (auto-fetches 10 articles per source)
```

#### **2. KoreanNewsResearchTool**
```python
Purpose: Fetch Korean economic/financial news from RSS feeds
Sources: 연합뉴스, 조선일보, 동아일보, 매일경제, 한국경제
Output: List of articles with {title, url, summary, published_date, source, category, importance_score}
Parameters: No input required (auto-fetches 10 articles per source)
```

#### **3. WebSearchTool**
```python
Purpose: Scrape full article content from URLs
Technology: Firecrawl API
Output: {title, url, content} - Full article text extracted from web pages
Parameters: url (string)
```

**Key Design Decision:** Tools use `feedparser` to parse RSS XML into structured Python objects, enabling consistent data extraction across diverse news sources.

---

### **👥 Agents (`news_crew.py`)**

The system employs three specialized agents with distinct responsibilities:

#### **1. Research Specialist Agent**
```
Role: Research Specialist
Goal: Collect latest news articles from RSS feeds
Tools: [global_news_research_tool, korean_news_research_tool]
Backstory: 20-year veteran at global news agency, expert at finding trending news

Responsibilities:
- Call RSS tools to fetch real-time news data
- Filter duplicates and irrelevant content
- Prioritize by importance and timeliness
```

#### **2. Senior Editor Agent**
```
Role: Senior Editor
Goal: Extract full article content and summarize key points
Tools: [web_search_tool]
Backstory: 15-year veteran editor, expert at content analysis and translation

Responsibilities:
- Access each article URL to extract full content
- Filter out advertisements and noise
- Translate English articles to Korean
- Summarize in 2-3 sentences
```

#### **3. News Curator Agent**
```
Role: News Curator
Goal: Select top 10 most important news and write final report
Tools: None (works with previous results)
Backstory: 10-year curation expert, expert at prioritization and reporting

Responsibilities:
- Analyze all edited articles
- Select top 10 by importance score (7+ preferred)
- Balance global/domestic ratio (30%/70%)
- Generate professional news briefing report
```

---

### **📋 Tasks (`news_crew.py`)**

The workflow consists of 4 sequential tasks:

#### **Task 1: Research Global News**
```yaml
Agent: Research Specialist
Description: Fetch latest global economic/financial news via RSS
Tools: [global_news_research_tool]
Output: output/global_news.json (max 10 articles)
```

#### **Task 2: Research Korean News**
```yaml
Agent: Research Specialist  
Description: Fetch latest Korean economic/financial news via RSS
Tools: [korean_news_research_tool]
Output: output/korean_news.json (max 10 articles)
```

#### **Task 3: Edit & Summarize Articles**
```yaml
Agent: Senior Editor
Description: Extract full content from URLs and create detailed summaries
Tools: [web_search_tool]
Input: Results from Task 1 & Task 2
Output: output/news_summary.json (all articles with full analysis)
```

#### **Task 4: Curate Final Briefing**
```yaml
Agent: News Curator
Description: Select top 10 most important news and format final report
Tools: None
Input: Results from Task 3
Output: output/final_news_briefing.md (formatted report)
Context: [edit_and_summarize_articles_task()]
```

### **Workflow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    Research Specialist                       │
├─────────────────────────────────────────────────────────────┤
│  Task 1: Global News  │  Task 2: Korean News               │
│  ├─ Call RSS Tool     │  ├─ Call RSS Tool                  │
│  ├─ Filter duplicates │  ├─ Filter duplicates              │
│  └─ Select top 10     │  └─ Select top 10                  │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           └──────────┬───────────┘
                      ▼
           ┌─────────────────────────┐
           │    Senior Editor        │
           ├─────────────────────────┤
           │ Task 3: Edit & Summary  │
           │ ├─ Scrape full content  │
           │ ├─ Translate to Korean  │
           │ └─ Summarize 2-3 sent.  │
           └───────────┬─────────────┘
                       ▼
           ┌─────────────────────────┐
           │    News Curator         │
           ├─────────────────────────┤
           │ Task 4: Final Curation  │
           │ ├─ Score importance     │
           │ ├─ Balance 3:7 ratio    │
           │ └─ Generate report      │
           └─────────────────────────┘
```

---

## 🤖 Telegram Bot Implementation (`bot.py`)

### **Development Methodology: Vibe Coding**

This bot was developed using **Vibe Coding** - an AI-assisted prompt-driven development approach where the entire implementation was generated from a structured specification document (`bot_prompt.md`).

### **Prompt Engineering Strategy**

The `bot_prompt.md` follows a hierarchical structure:

1. **Core Objective** - High-level goals
2. **Required Commands** - Detailed specifications for each command
3. **Technical Requirements** - Implementation constraints (timezone, message splitting)

This structured approach enabled the AI to generate production-ready code in a single pass, demonstrating the power of well-designed prompts.

### **Bot Features**

#### **Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message & command list | `/start` |
| `/get` | Instant news briefing | `/get` |
| `/schedule HH:MM` | Schedule daily briefing | `/schedule 09:00` |
| `/check` | View scheduled time | `/check` |
| `/cancel` | Cancel schedule | `/cancel` |

#### **Key Implementations**

**1. News Generation Integration**
```python
def kickoff_crew() -> str:
    news_crew = NewsCrew()
    result = news_crew.crew().kickoff()
    return result.raw
```
- Seamlessly integrates CrewAI workflow
- Returns final curated briefing as text

**2. Long Message Splitting**
```python
async def send_long_message(context, chat_id, text):
    # Splits messages >3000 chars at newline boundaries
    # Adds pagination "(2/5)" for multi-part messages
```
- Prevents Telegram's character limit issues
- Maintains message readability by splitting at natural breaks

**3. Timezone-Aware Scheduling**
```python
user_time = time(hour=naive_time.hour, minute=naive_time.minute, tzinfo=TIMEZONE)
context.job_queue.run_daily(send_scheduled_news, time=user_time, chat_id=chat_id)
```
- Uses `pytz` for accurate timezone handling
- Supports daily recurring briefings

### **TDD-Enhanced Vibe Coding**

During testing, the message splitting logic initially failed. This was resolved using **TDD (Test-Driven Development)** methodology:

1. **Problem Identified**: Message splitting at incorrect character boundaries
2. **Test Suite Created**: `tdd.py` with 6 test cases
3. **Iterative Refinement**: Fixed implementation to pass all tests
4. **Result**: ✅ All 6 tests passing with correct boundary handling

This hybrid approach combines the speed of Vibe Coding with the reliability of TDD, demonstrating pragmatic AI-assisted development.

---

## 🚀 Getting Started

### **Installation**

```bash
# Clone the repository
cd section_2

# Install dependencies using uv
uv sync

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys:
# - TELEGRAM_BOT_TOKEN
# - OPENAI_API_KEY
# - FIRECRAWL_API_KEY
```

### **Running the Bot**

```bash
# Direct execution (recommended due to pylance compatibility issue)
.venv/bin/python bot.py

# The bot will start polling for Telegram messages
```

### **Testing the Crew Workflow**

```bash
# Run standalone news generation
.venv/bin/python news_crew.py

# Check outputs in output/ directory:
# - output/global_news.json
# - output/korean_news.json
# - output/news_summary.json
# - output/final_news_briefing.md
```

---

## 📊 Results & Output

### **Sample Workflow Output**

The system generates structured outputs at each stage:

**Stage 1: RSS Collection**
- `global_news.json` - 20+ articles from Google News, BBC, CNN
- `korean_news.json` - 50+ articles from 5 Korean media outlets

**Stage 2: Content Extraction**
- `news_summary.json` - Full article content with translations and summaries

**Stage 3: Final Curation**
- `final_news_briefing.md` - Professional report with top 10 news stories

### **Telegram Bot in Action**


**/start command - Welcome message**

**/schedule command - Setting up daily briefing**
 
<img width="406" height="759" alt="Screenshot 2025-10-08 at 11 31 38 pm" src="https://github.com/user-attachments/assets/3fa7d991-47f3-4b57-b366-6d71d3c08d4f" />

<img width="414" height="303" alt="Screenshot 2025-10-08 at 11 31 54 pm" src="https://github.com/user-attachments/assets/ac000093-ea29-4591-a323-c495fb4345bf" />


**/get command - Instant briefing delivery, Final news briefing format**
<img width="907" height="701" alt="Screenshot 2025-10-08 at 11 35 18 pm" src="https://github.com/user-attachments/assets/eb77dde8-da33-41fb-9849-28090a4e9676" />

<img width="920" height="730" alt="Screenshot 2025-10-08 at 11 36 04 pm" src="https://github.com/user-attachments/assets/c29db275-d06f-4d3b-b399-d946d7085bbb" />

<img width="921" height="784" alt="Screenshot 2025-10-08 at 11 36 25 pm" src="https://github.com/user-attachments/assets/a122dfd3-6dd8-4203-bf94-beb31712551e" />


---

## 🏗️ Project Structure

```
section_2/
├── bot.py              # Telegram bot implementation
├── news_crew.py        # CrewAI multi-agent workflow
├── tool.py             # Custom RSS and web scraping tools
├── tdd.py              # Test suite for message splitting
├── env.py              # Environment configuration
├── bot_prompt.md       # Vibe Coding prompt specification
├── pyproject.toml      # Project dependencies
├── uv.lock             # Dependency lock file
└── output/             # Generated news reports
    ├── global_news.json
    ├── korean_news.json
    ├── news_summary.json
    └── final_news_briefing.md
```

---

## 💡 Key Learnings

### **1. Multi-Agent Collaboration**
CrewAI's agent framework enables complex workflows by breaking down tasks into specialized roles. Each agent focuses on its domain expertise, improving output quality.

### **2. Tool Design for LLM Agents**
Removing input parameters from RSS tools (making them parameter-free) significantly improved CrewAI's ability to correctly invoke them. LLMs sometimes struggle with complex tool schemas.

### **3. Vibe Coding + TDD = Best of Both Worlds**
- **Vibe Coding**: Rapid prototyping with AI-generated code from structured prompts
- **TDD**: Ensures correctness through systematic testing
- **Result**: Fast development with high reliability

### **4. RSS vs Web Scraping**
- **RSS feeds**: Fast, structured, but limited detail
- **Web scraping**: Complete content, but slower and more fragile
- **Hybrid approach**: Use RSS for discovery, scraping for depth

---

## 🔧 Troubleshooting

### **Permission Denied: `.config/crewai`**
If you encounter permission errors:
```bash
sudo mkdir -p ~/.config/crewai
sudo chown $(whoami):staff ~/.config/crewai
```

### **`pylance` installation error on macOS**
Use direct Python execution instead of `uv run`:
```bash
.venv/bin/python bot.py
```

### **Tool invocation failures**
Ensure tool input schemas are simple. Complex pydantic schemas may cause validation errors. Use `pass` for parameter-free tools.

---

## 📈 Future Enhancements

- [ ] Add sentiment analysis for news articles
- [ ] Implement user preference learning (favorite categories)
- [ ] Support multiple languages for briefings
- [ ] Add news source customization per user
- [ ] Integrate real-time breaking news alerts
- [ ] Add summarization quality metrics

---

## 📝 License

This project is developed as part of an AI Agent learning curriculum.

---

## 🙏 Acknowledgments

- **CrewAI** for the excellent multi-agent framework
- **python-telegram-bot** for robust Telegram bot capabilities
- **Firecrawl** for reliable web scraping
- **Feedparser** for RSS feed parsing

---

**Built with ❤️ using AI-assisted development (Vibe Coding + TDD)**
