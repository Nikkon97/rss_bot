from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    link = Column(String, nullable=False)
    published = Column(DateTime, default=func.now())
    source_id = Column(Integer, ForeignKey('sources.id'))
    source = relationship('Source')


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    sources = relationship('Source')
