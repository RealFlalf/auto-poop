# Telegram Bot

A Telegram bot that tracks users in a group chat and awards points when they use the /plus command.

## Features

- Tracks all users who join the group chat.
- Awards points and records timestamp when a user runs /plus command.
- Uses separate tables for users and scores to count total points.
- Uses SQLite database for data storage.
- Built with aiogram for modern async Telegram bot development.

## Setup

1. Create a new bot via [@BotFather](https://t.me/botfather) and get your BOT_TOKEN.
2. Clone or download this repository.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file and add your BOT_TOKEN:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   ```
5. Run the bot:
   ```
   python -m telegram_bot.main
   ```
   or using Docker:
   ```
   docker-compose up --build
   ```

## Usage

- Add the bot to your Telegram group as an administrator.
- The bot will automatically track users who join the chat.
- Type `/` to see available commands:
  - `/plus` - Add a point and see your total score.
  - `/stats` - View the top users by points (includes button to show growth chart for all users).
  - `/clear_scores` - Clear the scores table (admin only, username @tsed15).

## Best Practices Implemented

- Asynchronous programming with aiogram.
- SQLAlchemy for database ORM.
- Environment variables for configuration.
- Proper error handling and logging.
- Modular code structure.
