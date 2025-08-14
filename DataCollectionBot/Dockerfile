FROM python:3.12

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONPATH=/app:/app/src

CMD ["python", "src/data_collection_bot/main.py"]