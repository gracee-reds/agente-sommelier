import flet as ft

#Rutas de imágenes locales MODIFICAR
MAIL_IMG     = "imagenes/MAIL.png"
FONTANA_IMG  = "imagenes/fontanaIcono.png"
LETRAS_IMG   = "imagenes/letrasFontana.png"

MSG_COLOR      = "#9e8a77"
BUBBLE_BOT     = "#3d2e1e"
BUBBLE_USER    = "#5a3e28"
DARK_BG        = "#1a1209"
HEADER_BG      = "#13100d"
GOLD           = "#c9a96e"

BTN            = 70
BTN_R          = BTN // 2
PANEL_W        = 290
PANEL_H        = 300
CIRCLE_OVERLAP = BTN_R


def main(page: ft.Page):
    page.title = "Fontana Chatbox"
    page.window.width = 420
    page.window.height = 700
    page.window.resizable = False
    page.bgcolor = "#2a1f1a"
    page.padding = 0

    chat_panel_ref = ft.Ref[ft.Container]()
    messages_col   = ft.Ref[ft.Column]()
    text_input     = ft.Ref[ft.TextField]()

    def toggle_chat(e):
        chat_panel_ref.current.visible = not chat_panel_ref.current.visible
        page.update()

    def add_user_message(text: str):
        messages_col.current.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[
                    ft.Container(
                        bgcolor=BUBBLE_USER,
                        border_radius=ft.BorderRadius(
                            top_left=12, top_right=12,
                            bottom_left=12, bottom_right=4
                        ),
                        padding=ft.Padding(left=12, top=8, right=12, bottom=8),
                        content=ft.Text(text, color=MSG_COLOR, size=12),
                    )
                ],
            )
        )

    def add_bot_message(text: str):
        messages_col.current.controls.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.START,
                controls=[
                    ft.Container(
                        bgcolor=BUBBLE_BOT,
                        border_radius=ft.BorderRadius(
                            top_left=12, top_right=12,
                            bottom_left=4, bottom_right=12
                        ),
                        padding=ft.Padding(left=12, top=8, right=12, bottom=8),
                        content=ft.Text(text, color=MSG_COLOR, size=12),
                    )
                ],
            )
        )

    def on_bot_response(bot_reply: str):
        #APunto de entrada de datos para respuesta
        add_bot_message(bot_reply)
        page.update()

    def send_message(e):
        txt = text_input.current.value.strip()
        if not txt:
            return
        text_input.current.value = ""
        add_user_message(txt)
        page.update()

        #Sustituir Call
        on_bot_response("Recibido. ¿En qué más puedo ayudarte?")  # placeholder

    def mic_clicked(e):
        pass  # conectar reconocimiento de voz aquí

    header = ft.Container(
        bgcolor=HEADER_BG,
        border_radius=ft.BorderRadius(
            top_left=14, top_right=14, bottom_left=0, bottom_right=0
        ),
        padding=ft.Padding(left=10, top=10, right=14, bottom=10),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=FONTANA_IMG,
                        fit="cover",
                        width=28,
                        height=28,
                    ),
                ),
                ft.Container(width=5),
                ft.Image(src=LETRAS_IMG, height=24, fit="contain"),
                ft.Container(width=10),
                ft.Container(expand=True, height=1, bgcolor=MSG_COLOR),
            ]
        ),
    )

    messages_area = ft.Container(
        expand=True,
        bgcolor=DARK_BG,
        padding=ft.Padding(left=12, top=8, right=12, bottom=8),
        content=ft.Column(
            ref=messages_col,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=6,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    controls=[
                        ft.Container(
                            bgcolor=BUBBLE_BOT,
                            border_radius=ft.BorderRadius(
                                top_left=12, top_right=12,
                                bottom_left=4, bottom_right=12
                            ),
                            padding=ft.Padding(left=12, top=8, right=12, bottom=8),
                            content=ft.Text("¿Cómo podemos ayudarte?", color=MSG_COLOR, size=12),
                        )
                    ],
                ),
            ],
        ),
    )

    input_bar = ft.Container(
        bgcolor=HEADER_BG,
        border_radius=ft.BorderRadius(
            top_left=0, top_right=0, bottom_left=14, bottom_right=4
        ),
        padding=ft.Padding(left=10, top=8, right=CIRCLE_OVERLAP + 10, bottom=8),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor="#2a1f14",
                    border_radius=20,
                    padding=ft.Padding(left=12, top=2, right=4, bottom=2),
                    content=ft.TextField(
                        ref=text_input,
                        hint_text="Escribe aquí...",
                        hint_style=ft.TextStyle(color="#7a6a58", size=12),
                        color=MSG_COLOR,
                        text_size=12,
                        border=ft.InputBorder.NONE,
                        expand=True,
                        on_submit=send_message,
                        cursor_color=GOLD,
                        content_padding=ft.Padding(left=4, top=6, right=4, bottom=6),
                    ),
                ),
                ft.Container(
                    width=34,
                    height=34,
                    bgcolor=DARK_BG,
                    border_radius=17,
                    border=ft.border.all(1, GOLD),
                    ink=True,
                    on_click=mic_clicked,
                    content=ft.Icon(ft.Icons.MIC_NONE_ROUNDED, color=GOLD, size=17),
                ),
            ],
        ),
    )

    chat_panel = ft.Container(
        ref=chat_panel_ref,
        visible=False,
        width=PANEL_W,
        height=PANEL_H,
        bgcolor=DARK_BG,
        border_radius=ft.BorderRadius(
            top_left=16, top_right=16, bottom_left=16, bottom_right=4
        ),
        border=ft.border.all(1, "#5a4a38"),
        content=ft.Column(
            spacing=0,
            controls=[header, messages_area, input_bar],
        ),
    )

    toggle_button = ft.Container(
        width=BTN,
        height=BTN,
        bgcolor=MSG_COLOR,
        border_radius=BTN_R,
        border=ft.border.all(2, MSG_COLOR),
        ink=True,
        on_click=toggle_chat,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        content=ft.Image(src=MAIL_IMG, fit="contain", width=BTN, height=BTN),
    )

    STACK_W = PANEL_W + BTN_R
    STACK_H = PANEL_H + BTN_R

    chat_stack = ft.Stack(
        controls=[
            ft.Container(content=chat_panel, top=0, left=0),
            ft.Container(
                content=toggle_button,
                top=PANEL_H - BTN_R,
                left=PANEL_W - BTN_R,
            ),
        ],
        width=STACK_W,
        height=STACK_H,
    )

    page.add(
        ft.Container(
            expand=True,
            content=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.END,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    ft.Container(
                        content=chat_stack,
                        padding=ft.Padding(left=0, top=0, right=24, bottom=24),
                    )
                ],
            ),
        )
    )


ft.app(target=main)