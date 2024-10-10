FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r bot/requirements.txt

CMD ["python", "bot/bot.py"]