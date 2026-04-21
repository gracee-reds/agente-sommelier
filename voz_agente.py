import boto3
import speech_recognition as sr
import os
import time
import tempfile
from agente_vinos import chatear_con_sommelier, nueva_sesion

# Cliente de Polly para texto a voz
polly = boto3.client("polly", region_name="us-east-1")


def grabar_y_transcribir(segundos: int = 6, device_index: int = 1) -> str:
    """
    Graba audio del micrófono y lo convierte a texto.
    Usa Google Speech Recognition (gratuito, soporta es-MX).

    Parámetros:
        segundos     : duración máxima de grabación (default 6)
        device_index : índice del micrófono a usar (default 1 = Realtek integrado).
                       Cambiar según el dispositivo donde corra Flet.
                       Para ver dispositivos disponibles:
                           python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"

    Retorna:
        str — texto transcrito, o "" si no se detectó voz
    """
    reconocedor = sr.Recognizer()
    reconocedor.energy_threshold = 300
    reconocedor.dynamic_energy_threshold = False
    reconocedor.pause_threshold = 1.0

    try:
        with sr.Microphone(device_index=device_index) as fuente:
            print("Escuchando... habla ahora")
            audio = reconocedor.listen(
                fuente,
                timeout=8,
                phrase_time_limit=segundos
            )
            print("Procesando...")
            texto = reconocedor.recognize_google(audio, language="es-MX")
            return texto

    except sr.WaitTimeoutError:
        print("Tiempo agotado, no se detectó voz")
        return ""
    except sr.UnknownValueError:
        print("No se entendió el audio")
        return ""
    except sr.RequestError as e:
        print(f"Error de conexión: {e}")
        return ""


def texto_a_voz(texto: str) -> bytes:
    """
    Convierte texto a audio MP3 usando Amazon Polly.
    Voz: Mia Neural (español mexicano, femenina, sonido natural).

    Retorna:
        bytes — audio MP3 listo para reproducir
    """
    respuesta = polly.synthesize_speech(
        Text=texto,
        OutputFormat="mp3",
        VoiceId="Mia",
        LanguageCode="es-MX",
        Engine="neural"
    )
    return respuesta["AudioStream"].read()


def reproducir_audio(audio_bytes: bytes):
    """
    Reproduce audio MP3 sin abrir ventanas externas.
    Espera a que termine antes de continuar.
    Requiere: pip install pygame

    Nota para Flet:
        Si Flet tiene su propio widget de audio, puedes pasar audio_bytes
        directamente a ese widget en lugar de usar esta función.
    """
    import pygame

    tmp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    tmp.write(audio_bytes)
    tmp.close()

    pygame.mixer.init()
    pygame.mixer.music.load(tmp.name)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

    pygame.mixer.quit()
    os.unlink(tmp.name)


def sesion_de_voz():
    """
    Loop completo de conversación por voz para pruebas desde terminal.
    En Flet usar las funciones individuales:
        grabar_y_transcribir() → chatear_con_sommelier() → texto_a_voz() → reproducir_audio()
    """
    print("=== Modo voz del Sommelier Virtual ===")
    print("Presiona Ctrl+C para salir\n")

    sesion = nueva_sesion()

    resultado = chatear_con_sommelier("Hola", sesion)
    bienvenida = resultado["respuesta"]
    print(f"Viña: {bienvenida}\n")

    audio = texto_a_voz(bienvenida)
    reproducir_audio(audio)

    while True:
        try:
            texto_usuario = grabar_y_transcribir(segundos=6)

            if not texto_usuario:
                print("No te escuché, intenta de nuevo\n")
                audio = texto_a_voz("No te escuché, ¿podrías repetirlo?")
                reproducir_audio(audio)
                continue

            print(f"Tú: {texto_usuario}")

            resultado = chatear_con_sommelier(texto_usuario, sesion)
            respuesta = resultado["respuesta"]
            print(f"Viña: {respuesta}\n")

            audio = texto_a_voz(respuesta)
            reproducir_audio(audio)

            if resultado["whatsapp_url"]:
                print(f"Redirigiendo a WhatsApp: {resultado['whatsapp_url']}")
                break

        except KeyboardInterrupt:
            print("\nSesión de voz terminada")
            break


if __name__ == "__main__":
    sesion_de_voz()
