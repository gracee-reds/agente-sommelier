# Agente Sommelier Virtual — FONTANA

Agente conversacional de IA con voz construido sobre Amazon Bedrock.
Recomienda vinos, procesa órdenes y genera cotizaciones con integración a WhatsApp.
Incluye interfaz de chat flotante con soporte de voz.

## Inicio rápido

### Requisitos
- Python 3.11+
- AWS CLI instalado
- Credenciales AWS (se entregan por separado a los evaluadores)

### Instalación
```bash
pip install -r requirements.txt
aws configure
```

### Ejecutar agente por voz (terminal)
```bash
python voz_agente.py
```

### Ejecutar interfaz de chat
```bash
python chatbot_flotante.py
```

---

## Archivos del proyecto

| Archivo | Descripción |
|---|---|
| `agente_vinos.py` | Módulo principal — conexión a Amazon Bedrock |
| `voz_agente.py` | Módulo de voz — micrófono, Google Speech y Amazon Polly |
| `chatbot_flotante.py` | Interfaz de chat flotante con botón de micrófono |
| `requirements.txt` | Dependencias del proyecto |
| `imagenes/` | Assets visuales de la interfaz |

---

## Arquitectura
Usuario habla/escribe
↓
Google Speech Recognition (voz a texto)
↓
Amazon Bedrock — Agente Nova Pro
↓
AWS Lambda → Amazon RDS PostgreSQL
↓
Amazon Polly Neural — Voz Mia (texto a voz)
↓
WhatsApp (cotizaciones)

## Servicios AWS

| Servicio | Uso |
|---|---|
| Amazon Bedrock (Nova Pro) | Motor conversacional de IA |
| AWS Lambda | Consultas a base de datos |
| Amazon RDS PostgreSQL | Catálogo de vinos |
| Amazon Polly (Mia Neural) | Texto a voz en español mexicano |

## Integración con Flet

```python
from agente_vinos import chatear_con_sommelier, nueva_sesion
from voz_agente import grabar_y_transcribir, texto_a_voz, reproducir_audio

session_id = nueva_sesion()

# Modo chat
resultado = chatear_con_sommelier(texto_usuario, session_id)

# Modo voz
texto = grabar_y_transcribir()
resultado = chatear_con_sommelier(texto, session_id)
audio = texto_a_voz(resultado["respuesta"])
reproducir_audio(audio)

# WhatsApp automático
if resultado["whatsapp_url"]:
    page.launch_url(resultado["whatsapp_url"])
```

## Notas
- Las credenciales AWS se entregan por separado a los evaluadores
- Agent ID: `1FWAWL9025` | Alias: `3ON5PNBW3Y` | Región: `us-east-1`
- Voz: Mia Neural (español mexicano)
- El número de WhatsApp se configura en `agente_vinos.py`