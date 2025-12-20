FROM python:3.12-slim

# system deps
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements first for cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy app
COPY . .

# ensure data dirs exist
RUN mkdir -p data models

# expose API
EXPOSE 8000

# default command
CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8000"]
