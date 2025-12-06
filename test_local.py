"""
Script de Teste Local - Chatterbox TTS
======================================
Use este script para testar o voice cloning localmente antes de fazer deploy.

Requisitos:
    pip install chatterbox-tts torchaudio

Uso:
    python test_local.py
"""

import os
import sys

# Verificar se tem GPU
try:
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU disponível: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    else:
        print("⚠️ GPU não disponível, usando CPU (será lento)")
except ImportError:
    print("❌ PyTorch não instalado")
    sys.exit(1)

# Configurações do teste
TEXTO_TESTE = "No princípio, Deus criou os céus e a terra. E a terra era sem forma e vazia."

# Caminho para o áudio de referência (ajuste conforme necessário)
AUDIO_REF = "I:/Meu Drive/SISTEMAS/PROJETOS/VIDEO/VOICES/samples_librivox/bob_neufeld_republic.mp3"

# Arquivo de saída
OUTPUT_FILE = "teste_chatterbox_output.wav"


def main():
    print("\n" + "="*60)
    print("TESTE LOCAL - CHATTERBOX TTS")
    print("="*60)

    # Verificar áudio de referência
    if not os.path.exists(AUDIO_REF):
        print(f"❌ Áudio de referência não encontrado: {AUDIO_REF}")
        print("   Ajuste a variável AUDIO_REF no script")
        return

    print(f"\n📁 Áudio de referência: {os.path.basename(AUDIO_REF)}")
    print(f"📝 Texto: {TEXTO_TESTE[:50]}...")

    # Carregar modelo
    print("\n🔄 Carregando modelo Chatterbox...")
    from chatterbox.tts import ChatterboxTTS
    import torchaudio

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    print(f"✅ Modelo carregado no dispositivo: {device}")

    # Gerar áudio
    print("\n🎤 Gerando áudio...")
    print("   cfg_weight: 0.0 (português puro)")
    print("   exaggeration: 0.5 (expressividade média)")

    import time
    start_time = time.time()

    wav = model.generate(
        text=TEXTO_TESTE,
        audio_prompt_path=AUDIO_REF,
        cfg_weight=0.0,        # Português puro
        exaggeration=0.5       # Expressividade média
    )

    elapsed = time.time() - start_time
    print(f"✅ Geração completa em {elapsed:.1f} segundos")

    # Salvar
    torchaudio.save(OUTPUT_FILE, wav, model.sr)
    print(f"\n💾 Áudio salvo: {OUTPUT_FILE}")

    # Estatísticas
    duration = wav.shape[1] / model.sr
    print(f"\n📊 Estatísticas:")
    print(f"   Duração do áudio: {duration:.1f} segundos")
    print(f"   Sample rate: {model.sr} Hz")
    print(f"   Tempo de geração: {elapsed:.1f} segundos")
    print(f"   Ratio (real-time): {elapsed/duration:.2f}x")

    print("\n" + "="*60)
    print("TESTE COMPLETO!")
    print("="*60)


if __name__ == "__main__":
    main()
