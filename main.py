import html
import os

from telegram.constants import ParseMode
from telegram import Update, ReplyKeyboardMarkup
from telegram.error import BadRequest
from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL_NAME = "gemini-3.5-flash-lite"

client = None

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)




async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show the main menu."""
    context.user_data.pop("mode", None)

    keyboard = [
        ["💬 Ask anything"],
        ["📊 Analyze data", "📝 Summarize text"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
    )

    await update.message.reply_text(
        "Hello! I'm Nexora AI. 🤖\n\n"
        "Your AI assistant for questions, data analysis, "
        "and text summaries.\n\n"
        "Choose an option below or simply send me a message.\n\n"
        "Examples:\n"
        "• Do you understand Russian?\n"
        "• Calculate the conversion rate: 10 sales from 1,000 visitors.\n"
        "• Summarize: AI helps businesses save time.",
        reply_markup=reply_markup,
    )


async def analyze(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Analyze or summarize text with concise, formatted AI responses."""
    if client is None:
        await update.message.reply_text(
            "The AI service is not configured yet."
        )
        return

    user_text = " ".join(context.args).strip()
    command = update.message.text.split()[0].split("@")[0].lower()

    if not user_text:
        if command == "/summarize":
            message = (
                "Please provide text to summarize.\n\n"
                "Example:\n"
                "/summarize Your text goes here."
            )
        else:
            message = (
                "Please provide text to analyze.\n\n"
                "Example:\n"
                "/analyze Your text goes here."
            )

        await update.message.reply_text(message)
        return

    if command == "/summarize":
        task_instruction = """
Create a concise professional summary.
Use no more than 60 words.
Include only the main idea and essential points.
"""
    else:
        task_instruction = """
Act as a concise professional business analyst.
Use no more than 120 words.
Include only:
<b>Key metrics</b> — the most relevant figures.
<b>Formula</b> — show important calculations in a short
HTML preformatted block when calculations are relevant.
<b>Key insight</b> — the most important conclusion.
<b>Recommended action</b> — one practical next step.

Use only the sections relevant to the user's request.
Calculate carefully. Never invent data or benchmarks.
Clearly distinguish known facts from assumptions.
Avoid repeating the same information.
"""

    await update.message.reply_text("Analyzing...")

    try:
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=(
                "You are Nexora AI, a concise professional AI Analyst.\n"
                "Respond in the same language as the user's text.\n"
                "Return Telegram-compatible HTML, not Markdown.\n"
                "Allowed tags: <b>, <i>, <u>, <s>, <code>, <pre>, "
                "<blockquote>, <a href=\"...\">.\n"
                "Do not use Markdown markers such as **, ###, or ```.\n"
                "Do not use Markdown tables.\n"
                "Keep the response clean, readable, and brief.\n\n"
                f"Task:\n{task_instruction}\n\n"
                f"User text:\n{user_text}"
            ),
        )

        answer = response.text

        if not answer:
            await update.message.reply_text(
                "I couldn't generate a response. Please try again."
            )
            return

        answer = answer.strip()

        try:
            await update.message.reply_text(
                answer,
                parse_mode=ParseMode.HTML,
            )
        except BadRequest:
            # Fall back to safe plain text if the HTML is invalid.
            await update.message.reply_text(
                html.unescape(
                    answer.replace("<br>", "\n").replace("<br/>", "\n")
                )[:4000]
            )

    except Exception:
        await update.message.reply_text(
            "Sorry, I couldn't process your request right now. "
            "Please try again later."
        )


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Show the bot's available commands."""
    await update.message.reply_text(
        "Nexora AI — Your AI Assistant 🤖\n\n"
        "💬 Ask anything — Ask questions in your own words.\n"
        "📊 Analyze data — Analyze figures and calculate metrics.\n"
        "📝 Summarize text — Get a concise summary.\n\n"
        "Commands:\n"
        "/start — Open the main menu\n"
        "/help — Show this help message\n"
        "/analyze — Analyze data\n"
        "/summarize — Summarize text"
    )


async def handle_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """Handle menu selections and ordinary text messages."""
    user_text = update.message.text.strip()

    if user_text == "💬 Ask anything":
        context.user_data["mode"] = "chat"
        await update.message.reply_text(
            "Ask me anything in your own words.\n\n"
            "Example: Do you understand Russian?"
        )
        return

    if user_text == "📊 Analyze data":
        context.user_data["mode"] = "analyze"
        await update.message.reply_text(
            "Send the data you want me to analyze.\n\n"
            "Example: 1,000 visitors and 10 purchases per day."
        )
        return

    if user_text == "📝 Summarize text":
        context.user_data["mode"] = "summarize"
        await update.message.reply_text(
            "Send the text you want me to summarize.\n\n"
            "Example: AI helps businesses automate tasks."
        )
        return

    mode = context.user_data.pop("mode", "chat")

    if mode == "summarize":
        task = (
            "Summarize the text in no more than 60 words. "
            "Keep only the main ideas."
        )
    elif mode == "analyze":
        task = (
            "Analyze the input concisely in no more than 120 words. "
            "Include key findings, relevant calculations, and "
            "one practical recommendation when appropriate."
        )
    else:
        task = (
            "Answer the user's message directly and naturally. "
            "Be concise, helpful, and professional. "
            "Answer questions instead of summarizing them. "
            "Use the same language as the user."
        )

    await update.message.reply_text("Thinking... ⏳")

    try:
        response = await client.aio.models.generate_content(
            model=MODEL_NAME,
            contents=(
                "You are Nexora AI, a professional AI assistant "
                "and analyst.\n"
                "Return concise Telegram-compatible HTML. "
                "Do not use Markdown markers such as ** or ###. "
                "Use <b> for headings and <code> for short formulas. "
                "Do not invent facts or calculations.\n\n"
                f"Task: {task}\n\n"
                f"User message:\n{user_text}"
            ),
        )

        answer = response.text

        if not answer:
            await update.message.reply_text(
                "I couldn't generate a response. Please try again."
            )
            return

        await update.message.reply_text(
            answer[:4000],
            parse_mode=ParseMode.HTML,
        )

    except BadRequest:
        await update.message.reply_text(
            "I couldn't format the response correctly. "
            "Please try again."
        )

    except Exception:
        await update.message.reply_text(
            "Sorry, something went wrong. Please try again later."
        )

def main():
    """Configure and run the Telegram bot."""
    if not TELEGRAM_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN was not found in the .env file."
        )

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY was not found in the .env file."
        )

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("analyze", analyze))
    app.add_handler(CommandHandler("summarize", analyze))

    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
    )


    print("Nexora AI is running!")
    app.run_polling()


if __name__ == "__main__":
    main()
