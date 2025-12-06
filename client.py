"""
Cliente RunPod - Chatterbox TTS
===============================
Use este script para chamar o endpoint Chatterbox no RunPod.

Configuração:
    1. Defina as variáveis de ambiente:
       export RUNPOD_API_KEY="sua_api_key"
       export RUNPOD_ENDPOINT_ID="seu_endpoint_id"

    2. Ou edite as variáveis abaixo diretamente

Uso:
    python client.py "Texto para sintetizar" --voice bob_neufeld
"""

import os
import sys
import json
import time
import base64
import argparse
import requests
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO - Edite conforme necessário
# ============================================================

# API Key do RunPod (ou use variável de ambiente RUNPOD_API_KEY)
API_KEY = os.environ.get("RUNPOD_API_KEY", "SUA_API_KEY_AQUI")

# Endpoint ID (ou use variável de ambiente RUNPOD_ENDPOINT_ID)
ENDPOINT_ID = os.environ.get("RUNPOD_ENDPOINT_ID", "oa4tb12tnjuhmd")

# Diretório com os samples de voz
VOICES_DIR = Path("I:/Meu Drive/SISTEMAS/PROJETOS/VIDEO/VOICES/samples_librivox")

# Mapeamento de vozes disponíveis
VOICES = {
    # Vozes masculinas graves
    "bob_neufeld": "bob_neufeld_republic.mp3",
    "peter_eastman": "peter_eastman_dracula.mp3",
    "david_barnes": "david_barnes_imitation_christ.mp3",

    # Vozes masculinas médias
    "mark_smith": "mark_smith_sherlock_adventures.mp3",
    "david_clarke": "david_clarke_monte_cristo.mp3",

    # Vozes femininas
    "karen_savage": "karen_savage_pride_prejudice.mp3",
    "elizabeth_klett": "elizabeth_klett_jane_eyre.mp3",
    "ruth_golding": "ruth_golding_wuthering.mp3",
    "cori_samuel": "cori_samuel_frankenstein.mp3",
}

# URLs públicas dos samples (preencha após fazer upload)
# Exemplo: Google Cloud Storage, S3, etc.
VOICE_URLS = {
    # "bob_neufeld": "https://storage.googleapis.com/seu-bucket/bob_neufeld_republic.mp3",
}

# ============================================================
# CÓDIGO DO CLIENTE
# ============================================================

def get_voice_path(voice_name: str) -> Path:
    """Retorna o caminho do arquivo de voz"""
    if voice_name not in VOICES:
        raise ValueError(f"Voz '{voice_name}' não encontrada. Disponíveis: {list(VOICES.keys())}")
    return VOICES_DIR / VOICES[voice_name]


def get_voice_url(voice_name: str) -> str:
    """Retorna a URL pública da voz (se configurada)"""
    if voice_name in VOICE_URLS:
        return VOICE_URLS[voice_name]
    return None


def encode_audio_base64(file_path: Path) -> str:
    """Codifica arquivo de áudio em base64"""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def generate_speech(
    text: str,
    voice_name: str = "bob_neufeld",
    cfg_weight: float = 0.0,
    exaggeration: float = 0.5,
    use_url: bool = True,
    timeout: int = 300
) -> dict:
    """
    Gera áudio usando o endpoint RunPod

    Args:
        text: Texto a sintetizar
        voice_name: Nome da voz (ver VOICES)
        cfg_weight: 0.0 = português puro, 1.0 = mais sotaque
        exaggeration: 0.0 = neutro, 1.0 = expressivo
        use_url: Se True, usa URL; se False, envia base64
        timeout: Timeout em segundos

    Returns:
        dict com audio_base64, sample_rate, duration_seconds
    """
    # Preparar input
    input_data = {
        "text": text,
        "cfg_weight": cfg_weight,
        "exaggeration": exaggeration
    }

    # Obter referência de áudio
    voice_url = get_voice_url(voice_name)
    if use_url and voice_url:
        input_data["audio_ref_url"] = voice_url
        print(f"📡 Usando URL: {voice_url[:50]}...")
    else:
        voice_path = get_voice_path(voice_name)
        if not voice_path.exists():
            raise FileNotFoundError(f"Arquivo de voz não encontrado: {voice_path}")
        print(f"📦 Enviando áudio em base64...")
        input_data["audio_ref_base64"] = encode_audio_base64(voice_path)

    # Chamar endpoint (runsync para aguardar resultado)
    url = f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"🚀 Enviando requisição para RunPod...")
    start_time = time.time()

    response = requests.post(
        url,
        headers=headers,
        json={"input": input_data},
        timeout=timeout
    )

    elapsed = time.time() - start_time

    if response.status_code != 200:
        raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

    result = response.json()

    if result.get("status") == "FAILED":
        raise Exception(f"Job falhou: {result.get('error')}")

    if result.get("status") != "COMPLETED":
        raise Exception(f"Status inesperado: {result.get('status')}")

    output = result.get("output", {})
    if "error" in output:
        raise Exception(f"Erro no handler: {output['error']}")

    print(f"✅ Concluído em {elapsed:.1f}s")
    return output


def save_audio(audio_base64: str, output_path: str):
    """Salva áudio base64 em arquivo"""
    audio_data = base64.b64decode(audio_base64)
    with open(output_path, "wb") as f:
        f.write(audio_data)
    print(f"💾 Áudio salvo: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Cliente Chatterbox TTS - RunPod")
    parser.add_argument("text", help="Texto a sintetizar")
    parser.add_argument("--voice", "-v", default="bob_neufeld",
                        choices=list(VOICES.keys()),
                        help="Voz a usar (default: bob_neufeld)")
    parser.add_argument("--output", "-o", default="output.wav",
                        help="Arquivo de saída (default: output.wav)")
    parser.add_argument("--cfg-weight", "-c", type=float, default=0.0,
                        help="cfg_weight: 0.0=PT puro, 1.0=mais sotaque (default: 0.0)")
    parser.add_argument("--exaggeration", "-e", type=float, default=0.5,
                        help="Expressividade: 0.0=neutro, 1.0=expressivo (default: 0.5)")
    parser.add_argument("--use-base64", action="store_true",
                        help="Forçar envio em base64 (ignora URLs)")

    args = parser.parse_args()

    print("\n" + "="*60)
    print("CHATTERBOX TTS - CLIENTE RUNPOD")
    print("="*60)
    print(f"📝 Texto: {args.text[:50]}...")
    print(f"🎤 Voz: {args.voice}")
    print(f"⚙️  cfg_weight: {args.cfg_weight}")
    print(f"⚙️  exaggeration: {args.exaggeration}")
    print()

    try:
        result = generate_speech(
            text=args.text,
            voice_name=args.voice,
            cfg_weight=args.cfg_weight,
            exaggeration=args.exaggeration,
            use_url=not args.use_base64
        )

        save_audio(result["audio_base64"], args.output)

        print(f"\n📊 Resultado:")
        print(f"   Duração: {result.get('duration_seconds', '?')} segundos")
        print(f"   Sample rate: {result.get('sample_rate', '?')} Hz")

    except Exception as e:
        print(f"\n❌ Erro: {e}")
        sys.exit(1)

    print("\n" + "="*60)
    print("CONCLUÍDO!")
    print("="*60)


if __name__ == "__main__":
    main()
