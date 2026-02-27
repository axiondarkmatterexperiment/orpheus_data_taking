FROM python:3.12.3

WORKDIR /app
COPY . /app

RUN pip install fastapi uvicorn numpy blessed pytz psycopg2 scipy

CMD ["python", "main.py"]
