import time
import feedparser
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base, Source, News
from datetime import datetime

DATABASE_URL = 'postgresql://user:password@db/rss'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()


def fetch_news():
    sources = session.query(Source).all()
    for source in sources:
        feed = feedparser.parse(source.url)
        for entry in feed.entries:
            existing_news = session.query(News).filter(News.link == entry.link).first()
            if not existing_news:
                new_news = News(
                    title=entry.title,
                    link=entry.link,
                    source_id=source.id,
                    published=datetime(*entry.published_parsed[:6])
                )
                session.add(new_news)
        session.commit()


if __name__ == "__main__":
    while True:
        fetch_news()
        time.sleep(60)
