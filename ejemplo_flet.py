"""
INTEGRACIÓN DEL AGENTE SOMMELIER CON FLET
==========================================
Este archivo es un ejemplo funcional completo que muestra cómo conectar
el agente de vinos con una interfaz Flet que tiene:
  - Modo chat: barra de texto + botón enviar
  - Modo voz: botón de micrófono que graba, transcribe y reproduce respuesta

REQUISITOS
----------
Instalar dependencias:
    pip install flet boto3 SpeechRecognition pyaudio pygame

Configurar credenciales AWS (usar el archivo dev-flet_accessKeys.csv):
    aws configure
    > AWS Access Key ID: [valor del CSV]
    > AWS Secret Access Key: [valor del CSV]
    > Default region name: us-east-1
    > Default output format: json

NOTA IMPORTANTE — device_index del micrófono
---------------------------------------------
El device_index=1 en voz_agente.py corresponde al micrófono de la computadora
donde se desarrolló el agente. En otra computadora puede ser diferente.
Para encontrar el índice correcto ejecutar:
    python -c "import speech_recognition as sr; [print(i, sr.Microphone.list_microphone_names()[i]) for i in range(len(sr.Microphone.list_microphone_names()))]"
Luego cambiar el valor de device_index en voz_agente.py → grabar_y_transcribir()
"""

import flet as ft
import threading
from agente_vinos import chatear_con_sommelier, nueva_sesion
from voz_agente import grabar_y_transcribir, texto_a_voz, reproducir_audio


def main(page: ft.Page):
    page.title = "Sommelier Virtual"
    page.vertical_alignment = ft.MainAxisAlignment.END

    # ── Estado global de la sesión ─────────────────────────────────────────────
    session_id = nueva_sesion()
    escuchando = {"activo": False}

    # ── Componentes de UI ──────────────────────────────────────────────────────
    chat = ft.ListView(
        expand=True,
        spacing=10,
        padding=20,
        auto_scroll=True
    )

    campo_texto = ft.TextField(
        hint_text="Escribe tu mensaje aquí...",
        expand=True,
        on_submit=lambda e: enviar_mensaje(campo_texto.value)
    )

    boton_enviar = ft.IconButton(
        icon=ft.Icons.SEND,
        tooltip="Enviar mensaje",
        on_click=lambda e: enviar_mensaje(campo_texto.value)
    )

    boton_microfono = ft.IconButton(
        icon=ft.Icons.MIC,
        icon_color=ft.Colors.BLUE,
        tooltip="Hablar con el sommelier",
        on_click=lambda e: activar_voz()
    )

    indicador_estado = ft.Text(
        value="",
        color=ft.Colors.GREY_600,
        size=12,
        italic=True
    )

    # ── Funciones de UI ────────────────────────────────────────────────────────

    def agregar_burbuja_usuario(texto: str):
        """Agrega burbuja azul a la derecha (mensaje del usuario)."""
        chat.controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(texto, selectable=True),
                        padding=12,
                        border_radius=12,
                        bgcolor=ft.colors.BLUE_100,
                        max_width=380
                    )
                ],
                alignment=ft.MainAxisAlignment.END
            )
        )
        page.update()

    def agregar_burbuja_agente(texto: str):
        """Agrega burbuja gris a la izquierda (respuesta del sommelier)."""
        chat.controls.append(
            ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Text(texto, selectable=True),
                        padding=12,
                        border_radius=12,
                        bgcolor=ft.colors.GREY_200,
                        max_width=380
                    )
                ],
                alignment=ft.MainAxisAlignment.START
            )
        )
        page.update()

    def procesar_respuesta(resultado: dict):
        """
        Muestra la respuesta del agente en el chat.
        Si hay link de WhatsApp lo abre automáticamente.
        """
        agregar_burbuja_agente(resultado["respuesta"])
        if resultado["whatsapp_url"]:
            page.launch_url(resultado["whatsapp_url"])

    def enviar_mensaje(texto: str):
        """
        Modo chat: el usuario escribe y presiona Enter o el botón enviar.
        """
        if not texto.strip():
            return

        campo_texto.value = ""
        page.update()
        agregar_burbuja_usuario(texto)
        indicador_estado.value = "Sommelier pensando..."
        page.update()

        def llamar_agente():
            resultado = chatear_con_sommelier(texto, session_id)
            indicador_estado.value = ""
            procesar_respuesta(resultado)

        threading.Thread(target=llamar_agente, daemon=True).start()

    def activar_voz():
        """
        Modo voz: graba audio → transcribe → envía al agente → reproduce respuesta.
        Se activa al presionar el botón del micrófono.
        """
        if escuchando["activo"]:
            return

        def flujo_de_voz():
            escuchando["activo"] = True
            boton_microfono.icon_color = ft.colors.RED
            indicador_estado.value = "Escuchando..."
            page.update()

            # 1. Grabar y transcribir voz a texto
            texto = grabar_y_transcribir(segundos=6)

            if not texto:
                indicador_estado.value = "No te escuché, intenta de nuevo"
                boton_microfono.icon_color = ft.colors.BLUE
                escuchando["activo"] = False
                page.update()
                return

            # 2. Mostrar en chat lo que dijo el usuario
            agregar_burbuja_usuario(texto)
            indicador_estado.value = "Sommelier pensando..."
            page.update()

            # 3. Enviar al agente
            resultado = chatear_con_sommelier(texto, session_id)

            # 4. Mostrar respuesta en chat
            procesar_respuesta(resultado)

            # 5. Convertir respuesta a voz y reproducir
            indicador_estado.value = "Respondiendo..."
            page.update()
            audio_bytes = texto_a_voz(resultado["respuesta"])
            reproducir_audio(audio_bytes)

            # 6. Limpiar estado
            indicador_estado.value = ""
            boton_microfono.icon_color = ft.colors.BLUE
            escuchando["activo"] = False
            page.update()

        threading.Thread(target=flujo_de_voz, daemon=True).start()

    # ── Bienvenida automática al abrir la app ──────────────────────────────────
    def iniciar_bienvenida():
        resultado = chatear_con_sommelier("Hola", session_id)
        agregar_burbuja_agente(resultado["respuesta"])
        audio_bytes = texto_a_voz(resultado["respuesta"])
        reproducir_audio(audio_bytes)

    threading.Thread(target=iniciar_bienvenida, daemon=True).start()

    # ── Layout principal ───────────────────────────────────────────────────────
    page.add(
        ft.Container(content=chat, expand=True),
        indicador_estado,
        ft.Row(
            controls=[
                boton_microfono,
                campo_texto,
                boton_enviar
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
    )


ft.app(target=main)
