# Instrucciones de integración — Agente Sommelier Virtual

## Archivos que recibes

| Archivo | Qué es | Tocar? |
|---|---|---|
| `agente_vinos.py` | Conexión al agente de IA en AWS | NO |
| `voz_agente.py` | Micrófono, voz a texto y texto a voz | Solo `device_index` |
| `ejemplo_flet.py` | Ejemplo de cómo integrar en Flet | Es solo referencia |

---

## Paso 1 — Instalar dependencias

```powershell
pip install flet boto3 SpeechRecognition pyaudio pygame
```

---

## Paso 2 — Configurar credenciales AWS

Usa el archivo `dev-flet_accessKeys.csv` que te mandaron por separado:

```powershell
aws configure
```

Te pedirá 4 cosas:
```
AWS Access Key ID:     [columna "Access key ID" del CSV]
AWS Secret Access Key: [columna "Secret access key" del CSV]
Default region name:   us-east-1
Default output format: json
```

---

## Paso 3 — Verificar el micrófono

El `device_index=1` en `voz_agente.py` corresponde al micrófono de otra
computadora. Necesitas encontrar el índice correcto en la tuya:

```powershell
python -c "import speech_recognition as sr; [print(i, sr.Microphone.list_microphone_names()[i]) for i in range(len(sr.Microphone.list_microphone_names()))]"
```

Busca en la lista el micrófono que vas a usar (el integrado o uno externo).
Anota su número y cámbialo en `voz_agente.py`:

```python
# Línea a modificar en voz_agente.py → función grabar_y_transcribir()
with sr.Microphone(device_index=1) as fuente:  # <- cambia el 1 por tu índice
```

---

## Paso 4 — Probar que todo funciona

Antes de integrar con Flet, prueba el agente en la terminal:

```powershell
python voz_agente.py
```

Deberías escuchar la bienvenida de Mia y poder hablar con el agente.

---

## Paso 5 — Integrar en tu interfaz Flet

Importa las funciones en tu archivo principal de Flet:

```python
from agente_vinos import chatear_con_sommelier, nueva_sesion
from voz_agente import grabar_y_transcribir, texto_a_voz, reproducir_audio
```

### Iniciar sesión (hacer UNA vez al abrir la app)
```python
session_id = nueva_sesion()
```

### Modo chat (barra de texto)
```python
# Cuando el usuario envía un mensaje de texto:
resultado = chatear_con_sommelier(texto_del_usuario, session_id)

# resultado contiene:
# resultado["respuesta"]    → texto que muestra el agente en el chat
# resultado["whatsapp_url"] → link de WhatsApp si aplica (o None)

# Mostrar respuesta:
mi_burbuja_chat.value = resultado["respuesta"]

# Abrir WhatsApp si aplica:
if resultado["whatsapp_url"]:
    page.launch_url(resultado["whatsapp_url"])
```

### Modo voz (botón de micrófono)
```python
# Cuando el usuario presiona el botón de micrófono:

# 1. Grabar y convertir voz a texto
texto = grabar_y_transcribir(segundos=6)

# 2. Enviar al agente (igual que modo chat)
resultado = chatear_con_sommelier(texto, session_id)

# 3. Convertir respuesta a audio y reproducir
audio_bytes = texto_a_voz(resultado["respuesta"])
reproducir_audio(audio_bytes)

# 4. Abrir WhatsApp si aplica
if resultado["whatsapp_url"]:
    page.launch_url(resultado["whatsapp_url"])
```

### Importante — usar threading
Las llamadas al agente tardan 1-3 segundos. Para no congelar la UI
envuelve las llamadas en un hilo separado:

```python
import threading

def llamar_agente():
    resultado = chatear_con_sommelier(texto, session_id)
    # actualizar UI aquí

threading.Thread(target=llamar_agente, daemon=True).start()
```

---

## Referencia rápida

| Dato | Valor |
|---|---|
| Agent ID | `1FWAWL9025` |
| Agent Alias ID | `3ON5PNBW3Y` |
| Región AWS | `us-east-1` |
| Voz | Mia Neural (español mexicano) |
| Número WhatsApp | Pendiente de configurar en `agente_vinos.py` |

---

## Qué hace el agente automáticamente

1. Se presenta como sommelier virtual
2. Pregunta si quiere ordenar o cotizar
3. Si ordena: pregunta copa o botella → consulta BD → recomienda vinos
4. Si cotiza: consulta BD → recomienda → genera texto para WhatsApp
5. Al finalizar cotización: devuelve `whatsapp_url` en el resultado
