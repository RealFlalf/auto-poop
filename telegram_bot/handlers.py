import logging
import io
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import matplotlib.pyplot as plt
from telegram_bot.database import get_db, create_or_update_user, add_score, get_total_score, get_top_users, clear_scores, get_user_scores_over_time

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("plus"))
async def plus_command(message: types.Message):
    db = get_db()
    try:
        user = message.from_user
        # Создать или обновить пользователя
        create_or_update_user(
            db,
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        # Добавить очко
        add_score(db, user.id, 1)
        total_score = get_total_score(db, user.id)
        await message.reply(f"Привет! Ты получил +1 очко. Всего очков: {total_score}.")
    except Exception as e:
        logger.error(f"Error in plus_command: {e}")
        await message.reply("Произошла ошибка.")
    finally:
        db.close()

@router.message(Command("stats"))
async def stats_command(message: types.Message):
    db = get_db()
    try:
        top_users = get_top_users(db, 10)
        if not top_users:
            await message.reply("Нет пользователей с очками.")
            return

        response = "Топ пользователей по очкам:\n"
        for i, (telegram_id, username, first_name, last_name, total_score) in enumerate(top_users, 1):
            name = f"{first_name or ''} {last_name or ''}".strip() or username or f"User {telegram_id}"
            response += f"{i}. {name}: {total_score} очков\n"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Показать график роста очков", callback_data="show_chart")]
        ])
        await message.reply(response, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in stats_command: {e}")
        await message.reply("Произошла ошибка.")
    finally:
        db.close()

@router.message(Command("clear_scores"))
async def clear_scores_command(message: types.Message):
    user = message.from_user
    if user.username != "tsed15":
        await message.reply("У вас нет прав для выполнения этой команды.")
        return

    db = get_db()
    try:
        clear_scores(db)
        await message.reply("Таблица очков очищена.")
    except Exception as e:
        logger.error(f"Error in clear_scores_command: {e}")
        await message.reply("Произошла ошибка.")
    finally:
        db.close()

@router.callback_query(lambda c: c.data == "show_chart")
async def show_chart_callback(callback: types.CallbackQuery):
    db = get_db()
    try:
        data = get_user_scores_over_time(db)
        if not data:
            await callback.answer("Нет данных для графика.")
            return

        from collections import defaultdict
        user_data = defaultdict(lambda: defaultdict(int))

        for row in data:
            telegram_id, username, first_name, last_name, date, points = row
            name = f"{first_name or ''} {last_name or ''}".strip() or username or f"User {telegram_id}"
            user_data[name][date] += points

        plt.figure(figsize=(14, 10))
        colors = plt.cm.tab20.colors  # Использовать палитру цветов
        for i, (name, date_points) in enumerate(user_data.items()):
            dates = sorted(date_points.keys())
            cumulative = []
            total = 0
            for date in dates:
                total += date_points[date]
                cumulative.append(total)
            color = colors[i % len(colors)]
            plt.plot(dates, cumulative, marker='o', label=name, color=color, linewidth=2, markersize=6)

        plt.title('Рост очков пользователей со временем', fontsize=16, fontweight='bold')
        plt.xlabel('Дата', fontsize=14)
        plt.ylabel('Количество очков', fontsize=14)
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.legend(loc='upper left', fontsize=10, bbox_to_anchor=(1.05, 1))
        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        await callback.message.answer_photo(types.BufferedInputFile(buf.getvalue(), filename='chart.png'), caption="График роста очков пользователей")
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in show_chart_callback: {e}")
        await callback.answer("Ошибка при генерации графика.")
    finally:
        db.close()

@router.chat_member()
async def track_chat_members(chat_member: types.ChatMemberUpdated):
    db = get_db()
    try:
        user = chat_member.new_chat_member.user
        if chat_member.new_chat_member.status in ['member', 'administrator', 'creator']:
            # Пользователь присоединился или статус изменился
            create_or_update_user(
                db,
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name
            )
            logger.info(f"User {user.id} tracked in chat {chat_member.chat.id}")
    except Exception as e:
        logger.error(f"Error in track_chat_members: {e}")
    finally:
        db.close()
