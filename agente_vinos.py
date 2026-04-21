import boto3
import uuid
import urllib.parse

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────────
AGENT_ID        = "1FWAWL9025"
AGENT_ALIAS_ID  = "3ON5PNBW3Y"
REGION          = "us-east-1"
WHATSAPP_NUMBER = "521XXXXXXXXXX"  # Reemplazar con el número real del restaurante

# Cliente de Bedrock
bedrock_agent = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name=REGION
)


def nueva_sesion() -> str:
    """
    Genera un ID único de sesión.
    Llamar UNA VEZ cuando el usuario abre el chat o activa el modo voz.
    Guardar el valor y reutilizarlo en todos los mensajes de esa conversación.

    Ejemplo en Flet:
        session_id = nueva_sesion()
    """
    return str(uuid.uuid4())


def chatear_con_sommelier(mensaje: str, session_id: str) -> dict:
    """
    Envía un mensaje al agente y devuelve la respuesta.

    Parámetros:
        mensaje    : texto del usuario (puede venir de chat o de voz convertida a texto)
        session_id : ID de sesión generado con nueva_sesion()

    Retorna un dict con:
        {
            "respuesta"    : str        — texto de respuesta del agente
            "session_id"   : str        — mismo session_id recibido
            "whatsapp_url" : str | None — link de WhatsApp si aplica cotización
        }

    Ejemplo en Flet (modo chat):
        resultado = chatear_con_sommelier(campo_texto.value, session_id)
        burbuja_chat.value = resultado["respuesta"]
        if resultado["whatsapp_url"]:
            page.launch_url(resultado["whatsapp_url"])

    Ejemplo en Flet (modo voz):
        texto = grabar_y_transcribir()               # de voz_agente.py
        resultado = chatear_con_sommelier(texto, session_id)
        audio = texto_a_voz(resultado["respuesta"])  # de voz_agente.py
        reproducir_audio(audio)                      # de voz_agente.py
        if resultado["whatsapp_url"]:
            page.launch_url(resultado["whatsapp_url"])
    """
    try:
        respuesta_bedrock = bedrock_agent.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=mensaje
        )

        texto = ""
        for evento in respuesta_bedrock["completion"]:
            if "chunk" in evento:
                texto += evento["chunk"]["bytes"].decode("utf-8")

        whatsapp_url = None
        if "wa.me" in texto or "WhatsApp" in texto or "cotizar" in texto.lower():
            whatsapp_url = generar_link_whatsapp(texto)

        return {
            "respuesta": texto,
            "session_id": session_id,
            "whatsapp_url": whatsapp_url
        }

    except Exception as e:
        return {
            "respuesta": "Lo siento, ocurrió un error. Por favor intenta de nuevo.",
            "session_id": session_id,
            "whatsapp_url": None
        }


def generar_link_whatsapp(texto_cotizacion: str) -> str:
    """
    Genera el link de WhatsApp con el resumen de cotización prellenado.
    En Flet abrir con: page.launch_url(url)
    """
    texto_codificado = urllib.parse.quote(texto_cotizacion)
    return f"https://wa.me/{WHATSAPP_NUMBER}?text={texto_codificado}"
