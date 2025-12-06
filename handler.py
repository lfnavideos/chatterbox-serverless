"""
Chatterbox TTS Multilingual - RunPod Serverless Handler
=======================================================
Template customizado para o projeto "A Bíblia em Vídeos"

IMPORTANTE: Usa o modelo MULTILINGUAL para suporte a português!

Suporta:
- 23 idiomas incluindo PORTUGUÊS (pt)
- Áudio de referência via URL direta (MP3, WAV)
- Áudio de referência via base64
- Cross-lingual voice cloning
- Controle de emoção (exaggeration)

Idiomas suportados:
ar, da, de, el, en, es, fi, fr, he, hi, it, ja, ko,
ms, nl, no, pl, pt, ru, sv, sw, tr, zh

Autor: Projeto Bíblia em Vídeos
Data: 2025-12-06
"""

import runpod
import torch
import torchaudio
import base64
import io
import os
import tempfile
import requests
from typing import Optional

# Variável global para o modelo (carrega uma vez, reutiliza)
MODEL = None

# Idiomas suportados pelo modelo multilingual
SUPPORTED_LANGUAGES = [
    "ar", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi",
    "it", "ja", "ko", "ms", "nl", "no", "pl", "pt", "ru", "sv",
    "sw", "tr", "zh"
]

def get_model():
    """Carrega o modelo Chatterbox MULTILINGUAL (singleton pattern)"""
    global MODEL
    if MODEL is None:
        print("🔄 Carregando modelo Chatterbox MULTILINGUAL...")
        # IMPORTANTE: Usar ChatterboxMultilingualTTS para suporte a português!
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        device = "cuda" if torch.cuda.is_available() else "cpu"
        MODEL = ChatterboxMultilingualTTS.from_pretrained(device=device)
        print(f"✅ Modelo MULTILINGUAL carregado no dispositivo: {device}")
    return MODEL


def download_audio(url: str, timeout: int = 60) -> bytes:
    """Baixa áudio de uma URL"""
    print(f"📥 Baixando áudio de: {url[:50]}...")
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    print(f"✅ Download completo: {len(response.content)} bytes")
    return response.content


def save_temp_audio(audio_data: bytes, suffix: str = ".mp3") -> str:
    """Salva áudio em arquivo temporário"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(audio_data)
    temp_file.close()
    return temp_file.name


def generate_speech(
    text: str,
    audio_ref_path: str,
    language_id: str = "pt",
    cfg_weight: float = 0.5,
    exaggeration: float = 0.5
) -> bytes:
    """
    Gera áudio com voice cloning MULTILINGUAL

    Args:
        text: Texto a ser sintetizado
        audio_ref_path: Caminho para o áudio de referência
        language_id: Código do idioma (pt = português)
        cfg_weight: Peso do CFG (0.0 a 1.0)
        exaggeration: Controle de emoção (0.0 = neutro, 1.0 = expressivo)

    Returns:
        Áudio WAV em bytes
    """
    model = get_model()

    print(f"🎤 Gerando áudio MULTILINGUAL...")
    print(f"   Texto: {text[:50]}...")
    print(f"   Idioma: {language_id}")
    print(f"   cfg_weight: {cfg_weight}")
    print(f"   exaggeration: {exaggeration}")

    # Gerar áudio com modelo MULTILINGUAL
    # O parâmetro language_id é CRUCIAL para português!
    wav = model.generate(
        text=text,
        audio_prompt_path=audio_ref_path,
        language_id=language_id,
        cfg_weight=cfg_weight,
        exaggeration=exaggeration
    )

    # Converter para bytes
    buffer = io.BytesIO()
    torchaudio.save(buffer, wav, model.sr, format="wav")
    buffer.seek(0)

    print(f"✅ Áudio gerado: {buffer.getbuffer().nbytes} bytes")
    return buffer.read()


def handler(event: dict) -> dict:
    """
    Handler principal do RunPod Serverless

    Input esperado:
    {
        "input": {
            "text": "No princípio, Deus criou os céus e a terra.",

            // Opção 1: URL direta do áudio de referência
            "audio_ref_url": "https://exemplo.com/voz_referencia.mp3",

            // Opção 2: Áudio em base64
            "audio_ref_base64": "UklGRi...",

            // Parâmetros opcionais
            "language_id": "pt",        // IMPORTANTE: idioma do texto (default: pt)
            "cfg_weight": 0.5,          // Peso do CFG
            "exaggeration": 0.5,        // 0.0 = neutro, 1.0 = expressivo
            "output_format": "wav"      // wav ou mp3 (futuro)
        }
    }

    Output:
    {
        "audio_base64": "UklGRi...",
        "sample_rate": 24000,
        "duration_seconds": 5.2,
        "language_id": "pt"
    }
    """
    try:
        input_data = event.get("input", {})

        # Validar input
        text = input_data.get("text")
        if not text:
            return {"error": "Campo 'text' é obrigatório"}

        audio_ref_url = input_data.get("audio_ref_url")
        audio_ref_base64 = input_data.get("audio_ref_base64")

        if not audio_ref_url and not audio_ref_base64:
            return {"error": "Forneça 'audio_ref_url' ou 'audio_ref_base64'"}

        # Parâmetros opcionais
        language_id = input_data.get("language_id", "pt")  # Default: português!
        cfg_weight = float(input_data.get("cfg_weight", 0.5))
        exaggeration = float(input_data.get("exaggeration", 0.5))

        # Validar idioma
        if language_id not in SUPPORTED_LANGUAGES:
            return {
                "error": f"Idioma '{language_id}' não suportado. Suportados: {SUPPORTED_LANGUAGES}"
            }

        # Obter áudio de referência
        temp_audio_path = None
        try:
            if audio_ref_url:
                # Baixar da URL
                audio_data = download_audio(audio_ref_url)
                # Detectar extensão
                suffix = ".mp3" if ".mp3" in audio_ref_url.lower() else ".wav"
                temp_audio_path = save_temp_audio(audio_data, suffix)
            else:
                # Decodificar base64
                audio_data = base64.b64decode(audio_ref_base64)
                temp_audio_path = save_temp_audio(audio_data, ".mp3")

            # Gerar áudio
            output_audio = generate_speech(
                text=text,
                audio_ref_path=temp_audio_path,
                language_id=language_id,
                cfg_weight=cfg_weight,
                exaggeration=exaggeration
            )

            # Calcular duração
            model = get_model()
            duration = len(output_audio) / (model.sr * 2)  # 16-bit = 2 bytes/sample

            # Retornar resultado
            return {
                "audio_base64": base64.b64encode(output_audio).decode("utf-8"),
                "sample_rate": model.sr,
                "duration_seconds": round(duration, 2),
                "language_id": language_id
            }

        finally:
            # Limpar arquivo temporário
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}


# Iniciar servidor RunPod
if __name__ == "__main__":
    print("🚀 Iniciando Chatterbox TTS MULTILINGUAL Serverless...")
    print("📋 Parâmetros suportados:")
    print("   - text: Texto a sintetizar (obrigatório)")
    print("   - audio_ref_url: URL do áudio de referência")
    print("   - audio_ref_base64: Áudio de referência em base64")
    print("   - language_id: Idioma do texto (default: pt)")
    print(f"     Suportados: {SUPPORTED_LANGUAGES}")
    print("   - cfg_weight: 0.0 a 1.0 (default: 0.5)")
    print("   - exaggeration: 0.0 (neutro) a 1.0 (expressivo)")

    runpod.serverless.start({"handler": handler})
