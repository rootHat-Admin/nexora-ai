# Nexora AI

An AI-powered Telegram assistant built with Python and Google's Gemini API.

![Nexora AI](Nexora.jpg)

## Features

- AI-powered question answering
- Text analysis and summarization
- Structured, easy-to-read responses
- Telegram keyboard menu
- Google Gemini API integration

## Tech Stack

- Python
- Telegram Bot API
- python-telegram-bot
- Google Gemini API
- python-dotenv

## Setup

1. Clone this repository.
2. Create and activate a virtual environment.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`.
5. Add your API credentials to `.env`:

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   GEMINI_API_KEY=your_gemini_api_key
   ```

6. Run the bot:

   ```bash
   python main.py
   ```

## Security

Keep your API keys private. Never commit your `.env` file.

## Project Status

This project is under active development.
