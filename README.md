# Chatterbox TTS - RunPod Serverless

Template customizado para geração de voz com voice cloning cross-lingual.

## Funcionalidades

- ✅ Voice cloning a partir de URL de áudio
- ✅ Voice cloning a partir de áudio em base64
- ✅ Cross-lingual: voz em inglês → fala em português (ou qualquer idioma)
- ✅ Controle de emoção (exaggeration)
- ✅ Controle de sotaque (cfg_weight)

## Deploy no RunPod

### Opção 1: Via GitHub (Recomendado)

1. Faça fork deste repositório para sua conta GitHub
2. Acesse [RunPod Console](https://console.runpod.io/serverless)
3. Clique em **New Endpoint**
4. Selecione **GitHub Repo**
5. Cole a URL do seu fork
6. Configure:
   - **GPU:** 24 GB
   - **Max Workers:** 2
   - **Idle Timeout:** 5 segundos
7. Clique em **Deploy**

### Opção 2: Via Docker Hub

```bash
# Build local
docker build -t seu-usuario/chatterbox-serverless .

# Push para Docker Hub
docker push seu-usuario/chatterbox-serverless:latest
```

No RunPod, use a imagem `seu-usuario/chatterbox-serverless:latest`

## Uso da API

### Endpoint

```
POST https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync
```

### Headers

```
Authorization: Bearer {API_KEY}
Content-Type: application/json
```

### Request Body

```json
{
  "input": {
    "text": "No princípio, Deus criou os céus e a terra.",
    "audio_ref_url": "https://seu-storage.com/bob_neufeld_republic.mp3",
    "cfg_weight": 0.0,
    "exaggeration": 0.5
  }
}
```

### Parâmetros

| Parâmetro | Tipo | Obrigatório | Default | Descrição |
|-----------|------|-------------|---------|-----------|
| `text` | string | ✅ | - | Texto a ser sintetizado |
| `audio_ref_url` | string | ⚠️ | - | URL do áudio de referência |
| `audio_ref_base64` | string | ⚠️ | - | Áudio de referência em base64 |
| `cfg_weight` | float | ❌ | 0.0 | 0.0 = português puro, 1.0 = mais sotaque |
| `exaggeration` | float | ❌ | 0.5 | 0.0 = neutro, 1.0 = muito expressivo |

⚠️ Forneça `audio_ref_url` OU `audio_ref_base64`

### Response

```json
{
  "id": "job-123",
  "status": "COMPLETED",
  "output": {
    "audio_base64": "UklGRi...",
    "sample_rate": 24000,
    "duration_seconds": 5.2
  }
}
```

## Exemplos de Código

### Python

```python
import requests
import base64

API_KEY = "sua_api_key"
ENDPOINT_ID = "seu_endpoint_id"

# Gerar áudio
response = requests.post(
    f"https://api.runpod.ai/v2/{ENDPOINT_ID}/runsync",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "input": {
            "text": "No princípio, Deus criou os céus e a terra.",
            "audio_ref_url": "https://storage.com/bob_neufeld.mp3",
            "cfg_weight": 0.0,
            "exaggeration": 0.5
        }
    }
)

result = response.json()

# Salvar áudio
if result.get("status") == "COMPLETED":
    audio_data = base64.b64decode(result["output"]["audio_base64"])
    with open("output.wav", "wb") as f:
        f.write(audio_data)
    print(f"Áudio salvo! Duração: {result['output']['duration_seconds']}s")
```

### JavaScript/Node.js

```javascript
const fetch = require('node-fetch');
const fs = require('fs');

const API_KEY = "sua_api_key";
const ENDPOINT_ID = "seu_endpoint_id";

async function generateSpeech() {
  const response = await fetch(
    `https://api.runpod.ai/v2/${ENDPOINT_ID}/runsync`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        input: {
          text: "No princípio, Deus criou os céus e a terra.",
          audio_ref_url: "https://storage.com/bob_neufeld.mp3",
          cfg_weight: 0.0,
          exaggeration: 0.5
        }
      })
    }
  );

  const result = await response.json();

  if (result.status === "COMPLETED") {
    const audioBuffer = Buffer.from(result.output.audio_base64, 'base64');
    fs.writeFileSync('output.wav', audioBuffer);
    console.log(`Áudio salvo! Duração: ${result.output.duration_seconds}s`);
  }
}

generateSpeech();
```

## Parâmetro cfg_weight (Cross-Lingual)

O `cfg_weight` controla quanto da "identidade de idioma" original é mantida:

| cfg_weight | Resultado |
|------------|-----------|
| **0.0** | Português natural, sem sotaque estrangeiro |
| **0.3** | Leve sotaque, mais características da voz original |
| **0.5** | Mistura equilibrada |
| **1.0** | Máxima fidelidade à voz, possível sotaque forte |

**Recomendação para narração bíblica:** `cfg_weight=0.0`

## Parâmetro exaggeration (Emoção)

Controla a expressividade emocional da fala:

| exaggeration | Uso Recomendado |
|--------------|-----------------|
| **0.0-0.3** | Narração calma, textos contemplativos |
| **0.4-0.6** | Narração padrão, histórias |
| **0.7-0.9** | Momentos dramáticos, diálogos intensos |
| **1.0** | Máxima expressividade |

## Custos Estimados

| Duração do Áudio | Tempo GPU | Custo (24GB @ $0.00019/s) |
|------------------|-----------|---------------------------|
| 10 segundos | ~10-15s | ~$0.002 |
| 30 segundos | ~20-30s | ~$0.005 |
| 60 segundos | ~40-60s | ~$0.010 |

**Cold start inicial:** ~3-4 minutos (primeira requisição)

## Troubleshooting

### Job fica "IN_QUEUE" por muito tempo
- Primeira execução demora ~3-4 min (download do modelo)
- Verifique se a GPU tem 24GB+ de VRAM

### Erro "out of memory"
- Reduza o tamanho do texto
- Use GPU com mais VRAM

### Áudio com sotaque estranho
- Reduza `cfg_weight` para 0.0
- Use áudio de referência mais longo (10-30s)

## Licença

- **Chatterbox:** MIT License (uso comercial permitido)
- **Este template:** MIT License

---

*Template criado para o projeto "A Bíblia em Vídeos"*
*Data: 2025-12-05*
