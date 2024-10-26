from flet import *
import os

def main(page: Page):
    page.title = "画像ドラッグ&ドロップ"
    page.window_width = 600
    page.window_height = 400
    
    # ドロップされた画像を表示するコンテナ
    img_preview = Image(
        width=280,
        height=280,
        fit=ImageFit.CONTAIN,
        visible=False
    )
    
    drop_text = Text("ここに画像をドロップしてください", size=16, color=colors.GREY_400)
    
    container = Container(
        width=300,
        height=300,
        border=border.all(2, colors.BLUE_400),
        border_radius=10,
        alignment=alignment.center,
        content=Stack([drop_text, img_preview])
    )

    def on_upload_progress(e: FilePickerUploadEvent):
        if e.progress == 1:  # アップロード完了
            file_path = os.path.join(os.path.dirname(__file__), e.file_name)
            if e.file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                drop_text.visible = False
                img_preview.visible = True
                img_preview.src = file_path
                page.update()
            else:
                page.show_snack_bar(SnackBar(
                    content=Text("画像ファイルのみ対応しています"),
                    duration=3000
                ))

    # ファイルピッカーの設定
    file_picker = FilePicker(
        on_upload=on_upload_progress
    )
    page.overlay.append(file_picker)
    
    # ドロップターゲットの設定
    drop_target = Container(
        content=container,
    )

    page.add(
        Column(
            controls=[
                Text("画像ドラッグ&ドロップデモ", size=24, weight=FontWeight.BOLD),
                drop_target,
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        )
    )

if __name__ == '__main__':
    app(target=main)