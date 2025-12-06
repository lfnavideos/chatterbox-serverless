FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    torch==2.6.0 \
    torchaudio==2.6.0 \
    --index-url https://download.pytorch.org/whl/cu124

RUN pip install --no-cache-dir \
    "chatterbox-tts @ git+https://github.com/travisvn/chatterbox-multilingual.git@exp"

RUN pip install --no-cache-dir \
    runpod \
    requests \
    soundfile

COPY handler.py /app/handler.py

ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "/app/handler.py"]
