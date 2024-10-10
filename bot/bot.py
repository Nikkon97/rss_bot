import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Source, News, User
from datetime import datetime, timedelta

API_TOKEN = 'YOUR_BOT_API_TOKEN'  # Здесь нужно будет указать токен вашего бота
MAX_MESSAGE_LENGTH = 4096

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

DATABASE_URL = 'postgresql://user:password@db/rss'
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Session = sessionmaker(bind=engine)
session = Session()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Привет! Я помогу тебе следить за новостями.")


@dp.message_handler(commands=['add_source'])
async def add_source(message: types.Message):
    await message.reply("Пришли мне URL источника.")

    @dp.message_handler(lambda msg: msg.from_user.id == message.from_user.id)
    async def process_url(msg: types.Message):
        url = msg.text

        user = session.query(User).filter(User.id == message.from_user.id).first()
        if not user:
            user = User(id=message.from_user.id, username=message.from_user.username)
            session.add(user)
            session.commit()

        existing_source = session.query(Source).filter(Source.url == url).first()
        if not existing_source:
            new_source = Source(url=url, user_id=message.from_user.id)
            session.add(new_source)
            session.commit()
            await msg.reply("Источник добавлен!")
        else:
            await msg.reply("Этот источник уже добавлен.")

        dp.message_handlers.unregister(process_url)


@dp.message_handler(commands=['get_news_hour'])
async def get_news_hour(message: types.Message):
    now = datetime.utcnow()
    one_hour_ago = now - timedelta(hours=1)
    news = session.query(News).filter(News.published >= one_hour_ago).all()
    if news:
        response = "\n\n".join([f"{n.title}\n{n.link}" for n in news])
        if len(response) > MAX_MESSAGE_LENGTH:
            for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                await message.reply(response[i:i + MAX_MESSAGE_LENGTH])
    else:
        await message.reply("Новостей за последний час нет.")


@dp.message_handler(commands=['get_news_day'])
async def get_news_day(message: types.Message):
    now = datetime.utcnow()
    one_day_ago = now - timedelta(days=1)
    news = session.query(News).filter(News.published >= one_day_ago).all()
    if news:
        response = "\n\n".join([f"{n.title}\n{n.link}" for n in news])
        if len(response) > MAX_MESSAGE_LENGTH:
            for i in range(0, len(response), MAX_MESSAGE_LENGTH):
                await message.reply(response[i:i + MAX_MESSAGE_LENGTH])
    else:
        await message.reply("Новостей за последние сутки нет.")


@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    await message.reply(
        "Доступные команды:\n/add_source — добавить источник\n/get_news_hour — новости за последний час\n/get_news_day — новости за сутки\n/help — помощь")


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    executor.start_polling(dp, skip_updates=True)
