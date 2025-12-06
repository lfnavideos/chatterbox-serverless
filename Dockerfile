FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

  WORKDIR /app

  # Instalar dependências do sistema
  RUN apt-get update && apt-get install -y \
      ffmpeg \
      libsndfile1 \
      git \
      && rm -rf /var/lib/apt/lists/*

  # Instalar numpy primeiro (necessário para pkuseg)
  RUN pip install --no-cache-dir numpy==1.26.0

  # Clonar e instalar chatterbox do source
  RUN git clone https://github.com/resemble-ai/chatterbox.git /tmp/chatterbox && \
      cd /tmp/chatterbox && \
      pip install --no-cache-dir -e . && \
      rm -rf /tmp/chatterbox/.git

  # Instalar dependências adicionais
  RUN pip install --no-cache-dir \
      runpod \
      requests \
      soundfile

  # Copiar handler
  COPY handler.py /app/handler.py

  # Definir variáveis de ambiente
  ENV PYTHONUNBUFFERED=1

  # Comando de execução
  CMD ["python", "-u", "/app/handler.py"]
