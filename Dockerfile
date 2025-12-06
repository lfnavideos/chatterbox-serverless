FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

  WORKDIR /app

  # Instalar dependências do sistema
  RUN apt-get update && apt-get install -y \
      ffmpeg \
      libsndfile1 \
      git \
      && rm -rf /var/lib/apt/lists/*

  # Instalar dependências básicas primeiro
  RUN pip install --no-cache-dir \
      runpod \
      requests \
      soundfile

  # Instalar chatterbox-tts (inclui torchaudio e outras dependências)
  RUN pip install --no-cache-dir chatterbox-tts

  # Copiar handler
  COPY handler.py /app/handler.py

  # Definir variáveis de ambiente
  ENV PYTHONUNBUFFERED=1

  # Comando de execução
  CMD ["python", "-u", "/app/handler.py"]
