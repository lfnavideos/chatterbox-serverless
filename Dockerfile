FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências Python
RUN pip install --no-cache-dir \
    runpod \
    chatterbox-tts \
    torchaudio \
    requests \
    soundfile

# Copiar handler
COPY handler.py /app/handler.py

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1

# Comando de execução
CMD ["python", "-u", "/app/handler.py"]
