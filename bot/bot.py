import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Source, News, User
from datetime import datetime, timedelta

API_TOKEN = 'YOUR_BOT_API_TOKEN'  # Здесь нужно будет указать токен вашего бота

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Логгирование
logging.basicConfig(level=logging.INFO)

# Подключение к базе данных
DATABASE_URL = 'postgresql://user:password@db/rss'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я помогу тебе следить за новостями.")


@dp.message_handler(commands=['add_source'])
async def add_source(message: types.Message):
    await message.reply("Пришли мне URL источника.")

    @dp.message_handler()
    async def process_url(msg: types.Message):
        url = msg.text
        existing_source = session.query(Source).filter(Source.url == url).first()
        if not existing_source:
            new_source = Source(url=url, user_id=message.from_user.id)
            session.add(new_source)
            session.commit()
            await msg.reply("Источник добавлен!")
        else:
            await msg.reply("Этот источник уже добавлен.")


@dp.message_handler(commands=['get_news_hour'])
async def get_news_hour(message: types.Message):
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    news = session.query(News).filter(News.published >= one_hour_ago).all()
    if news:
        response = "\n\n".join([f"{n.title}\n{n.link}" for n in news])
        await message.reply(response)
    else:
        await message.reply("Новостей за последний час нет.")


@dp.message_handler(commands=['get_news_day'])
async def get_news_day(message: types.Message):
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)
    news = session.query(News).filter(News.published >= one_day_ago).all()
    if news:
        response = "\n\n".join([f"{n.title}\n{n.link}" for n in news])
        await message.reply(response)
    else:
        await message.reply("Новостей за последние сутки нет.")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.reply(
        "Доступные команды:\n/add_source — добавить источник\n/get_news_hour — новости за последний час\n/get_news_day — новости за сутки\n/help — помощь")


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    executor.start_polling(dp, skip_updates=True)
