import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from .config import BOT_TOKEN
from .database import create_tables
from .handlers import router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Создание таблиц в БД
    create_tables()
    logger.info("Database tables created.")

    # Инициализация бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация роутера
    dp.include_router(router)

    # Установка команд
    await bot.set_my_commands([
        BotCommand(command="plus", description="Добавить очко"),
        BotCommand(command="stats", description="Показать статистику топ пользователей"),
        BotCommand(command="clear_scores", description="Очистить таблицу очков (только админ)")
    ])

    # Запуск бота
    logger.info("Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
