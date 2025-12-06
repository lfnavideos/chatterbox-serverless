FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

  WORKDIR /app

  RUN apt-get update && apt-get install -y \
      ffmpeg \
      libsndfile1 \
      git \
      && rm -rf /var/lib/apt/lists/*

  RUN pip install --no-cache-dir numpy==1.26.0

  RUN git clone https://github.com/resemble-ai/chatterbox.git /tmp/chatterbox && \
      cd /tmp/chatterbox && \
      pip install --no-cache-dir -e . && \
      rm -rf /tmp/chatterbox/.git

  RUN pip install --no-cache-dir \
      runpod \
      requests \
      soundfile

  COPY handler.py /app/handler.py

  ENV PYTHONUNBUFFERED=1

  CMD ["python", "-u", "/app/handler.py"]
