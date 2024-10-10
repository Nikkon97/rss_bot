FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install -r monitoring/requirements.txt

CMD ["python", "monitoring/monitor.py"]