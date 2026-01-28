FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x ./wait-for-it.sh

ENV PYTHONPATH=/app:/app/src

CMD ["python", "src/data_collection_bot/main.py"]