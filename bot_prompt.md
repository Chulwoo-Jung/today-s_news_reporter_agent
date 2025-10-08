You are an expert Telegram bot developer. Using python-telegram-bot library, develop a bot that provides daily news briefings.
Write a complete Python script (bot.py) following these requirements:

CORE OBJECTIVE
-------------
1. Provide instant news briefing on request
2. Allow scheduling daily briefings at user-specified times  
3. Provide interface to manage schedules

REQUIRED COMMANDS
----------------
Implement these 5 commands with user-friendly responses:

1. /start
- Welcome new users
- Show all available commands and examples
- Example: "Hello! I am the News Briefing Bot. 
  • /get → Get instant news briefing
  • /schedule HH:MM → Schedule daily news
  ..."

2. /get
- Immediately generate and send news briefing
- Show "Preparing your news briefing..." while processing
- Call kickoff_crew() to fetch news
- Use send_long_message helper for long content

3. /schedule HH:MM  
- Set/update daily schedule for specified time
- Validate HH:MM format
- Show usage guidance if invalid
- Only one active schedule per user
- Remove old schedule when setting new one
- Confirm with next run time and countdown

4. /check
- Show next scheduled briefing time
- If no schedule: "You have no scheduled briefings"

5. /cancel
- Cancel active schedule
- Confirm cancellation
- If no schedule: indicate nothing to cancel

TECHNICAL REQUIREMENTS
---------------------
1. Timezone
- Use 'Asia/Seoul' for all time calculations

2. Long Messages
- Split messages >4096 chars into 3000-char chunks
- Add page numbers "(2/N)" from second message

Write complete bot.py implementing all above requirements.