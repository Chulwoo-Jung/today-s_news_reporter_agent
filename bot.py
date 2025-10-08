import logging
import os
from datetime import datetime, time, timedelta
import pytz
from telegram import Update
from telegram.ext import (Application, CallbackContext, CommandHandler,
                          ContextTypes)

from news_crew import NewsCrew

# --- Configuration ---
# It's recommended to set this as an environment variable for security.
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TIMEZONE = pytz.timezone("Europe/Berlin")
MAX_MESSAGE_LENGTH = 3000


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- Placeholder for News Generation ---
def kickoff_crew() -> str:
    """
    This is a dummy function to simulate fetching and generating a news briefing.
    In a real application, this function would contain the logic to call a news API,
    process the data with a language model, and return the final text.
    """
    news_crew = NewsCrew()
    result = news_crew.crew().kickoff()
    return result


# --- Helper Functions ---
async def send_long_message(
    context: CallbackContext, chat_id: int, text: str
):
    """
    Splits a long message into chunks of MAX_MESSAGE_LENGTH and sends them sequentially.
    Adds a page counter (e.g., "(2/5)") to subsequent messages.
    """
    if len(text) <= MAX_MESSAGE_LENGTH:
        await context.bot.send_message(chat_id=chat_id, text=text)
        return

    parts = []
    while len(text) > 0:
        if len(text) > MAX_MESSAGE_LENGTH:
            part = text[:MAX_MESSAGE_LENGTH]
            # Find the last newline to avoid cutting words/sentences mid-way
            last_newline = part.rfind('\n')
            if last_newline != -1:
                parts.append(text[:last_newline])
                text = text[last_newline+1:]
            else:
                parts.append(part)
                text = text[MAX_MESSAGE_LENGTH:]
        else:
            parts.append(text)
            break

    total_parts = len(parts)
    for i, part in enumerate(parts):
        message = part
        if total_parts > 1:
            message = f"{part}\n\n({i + 1}/{total_parts})"
        await context.bot.send_message(chat_id=chat_id, text=message)


async def send_scheduled_news(context: CallbackContext):
    """
    Callback function executed by the job scheduler.
    Fetches news and sends it to the specified chat ID.
    """
    job = context.job
    chat_id = job.chat_id
    logger.info(f"Executing scheduled job for chat_id: {chat_id}")

    await context.bot.send_message(
        chat_id=chat_id, text="It's the scheduled time! Preparing today's news briefing..."
    )
    news_briefing = kickoff_crew()
    await send_long_message(context, chat_id, news_briefing)


# --- Command Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command. Displays a welcome message and command list."""
    user = update.effective_user
    help_text = (
        f"Hello, {user.first_name}! I am the News Briefing Bot.\n\n"
        "Available commands are as follows:\n\n"
        "▪️ /get\n"
        "   Get instant news briefing.\n\n"
        "▪️ /schedule HH:MM\n"
        "   Schedule daily news briefing at specified time (24-hour format).\n"
        "   Example: `/schedule 08:30`\n\n"
        "▪️ /check\n"
        "   Check your currently scheduled briefing time.\n\n"
        "▪️ /cancel\n"
        "   Cancel your scheduled news briefing."
    )
    await update.message.reply_text(help_text)


async def get_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /get command. Fetches and sends news immediately."""
    chat_id = update.effective_chat.id
    await context.bot.send_message(
        chat_id=chat_id, text="Preparing news briefing. Please wait a moment..."
    )
    news_briefing = kickoff_crew()
    await send_long_message(context, chat_id, news_briefing)


async def schedule_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /schedule command. Sets up a daily job."""
    chat_id = update.effective_chat.id
    
    # --- Input Validation ---
    if not context.args or len(context.args) != 1:
        await update.message.reply_text("Usage: Please enter time in `/schedule HH:MM` format.\nExample: `/schedule 09:00`", parse_mode='Markdown')
        return

    try:
        user_time_str = context.args[0]
        user_time = datetime.strptime(user_time_str, "%H:%M").time()
    except ValueError:
        await update.message.reply_text("Time format is incorrect. Please enter in `HH:MM` format.\nExample: `/schedule 22:30`", parse_mode='Markdown')
        return
    
    # --- Remove existing jobs to prevent duplicates ---
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
    if current_jobs:
        for job in current_jobs:
            job.schedule_removal()
        logger.info(f"Removed {len(current_jobs)} existing jobs for chat_id: {chat_id}")

    # --- Schedule the new job ---
    context.job_queue.run_daily(
        send_scheduled_news,
        time=user_time,
        chat_id=chat_id,
        name=str(chat_id),
        tzinfo=TIMEZONE
    )

    now = datetime.now(TIMEZONE)
    scheduled_dt = now.replace(hour=user_time.hour, minute=user_time.minute, second=0, microsecond=0)
    if scheduled_dt < now:
        scheduled_dt += timedelta(days=1)
    
    time_diff = scheduled_dt - now
    hours, remainder = divmod(time_diff.seconds, 3600)
    minutes = remainder // 60

    await update.message.reply_text(
        f"✅ Successfully scheduled!\n"
        f"Will send news briefing daily at `{user_time_str}`.\n"
        f"Next briefing will be sent in approximately {hours} hours and {minutes} minutes.",
        parse_mode='Markdown'
    )


async def check_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /check command. Reports the next scheduled job time."""
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))

    if not current_jobs:
        await update.message.reply_text("There is no scheduled news briefing.")
        return

    job = current_jobs[0]
    next_run_time = job.next_run_time.astimezone(TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')
    
    await update.message.reply_text(
        f"🗓️ You have a scheduled briefing.\n"
        f"Next execution time: {next_run_time} (Seoul Time)"
    )


async def cancel_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /cancel command. Removes the scheduled job."""
    chat_id = update.effective_chat.id
    current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))

    if not current_jobs:
        await update.message.reply_text("There is no scheduled briefing to cancel.")
        return

    for job in current_jobs:
        job.schedule_removal()

    await update.message.reply_text("✅ All news briefing schedules have been successfully cancelled.")


def run_bot():
    """Starts the bot."""
    if TELEGRAM_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN":
        logger.error("Telegram bot token not found. Please set the TELEGRAM_BOT_TOKEN environment variable.")
        return

    handlers = [
        CommandHandler("start", start),
        CommandHandler("get", get_news),
        CommandHandler("schedule", schedule_news),
        CommandHandler("check", check_schedule),
        CommandHandler("cancel", cancel_schedule),
    ]

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # --- Register Command Handlers ---
    for handler in handlers:
        application.add_handler(handler)

    application.run_polling()

