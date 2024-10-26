import flet as ft
import os
import dotenv
import anthropic
import base64
import webbrowser

def main(page: ft.Page):
    
    OUTPUT_FILE = "index.html"
    
    dotenv.load_dotenv()
    api_key = os.getenv("CLAUD_API_KEY")
    model = os.getenv("CLAUD_MODEL")
    
    #
    # Initialize Anthropic
    #
    client = anthropic.Anthropic(api_key=api_key)
    
    #
    # File Picker
    #
    file_picker = ft.FilePicker()
    page.overlay.append(file_picker)
    
    ##
    # processing message
    ##
    overlay = ft.Column(
        controls=[
            ft.Text("Processing...", size=36, color=ft.colors.BLUE_700), 
            ft.ProgressRing(),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        visible=False  # 初期状態では非表示
    )
    
    page.title = "Image Editor App"
    filepath_save = ""
    filename_save = ""
    fileimage_save = None
        
    # Load image file
    def load_image(e):
        
        file_picker.pick_files(allow_multiple=False)
        def on_file_pick_result(e: ft.FilePickerResultEvent):
            nonlocal filepath_save
            nonlocal filename_save 
            nonlocal fileimage_save
            if e.files:
                for f in e.files:
                    print(f"Selected file: {f.name}, {f.path}")
                    filepath_save = f.path
                    filename_save = f.name
                    fileimage_save = ft.Image(src=f.path,key=filename_save)
                    page.add(fileimage_save)

            else:
                print("File picking cancelled.")
            page.update()

        file_picker.on_result = on_file_pick_result
    
    # Generate HTML and CSS using Claud's API
    def generate_html_css(e):
        base64_encoded = ""
        with open(filepath_save, "rb") as file:
            file_content = file.read()
            base64_encoded = base64.b64encode(file_content).decode('utf-8')
        
        overlay.visible = True
        page.update()
        image_media_type = "image/png" 
        response = client.messages.create(
                    model=model,
                    system="You are an Web Designer and image editor. You can edit the image. You can also return only HTML include CSS. no Explanation just code.",
                    max_tokens=4096,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": image_media_type,
                                        "data": base64_encoded,
                                    },
                                },
                                {
                                    "type": "text",
                                    "text": "Create HTML include CSS  from the image of this  and return only HTML include CSS. no Explanation just code.",
                                }
                            ],
                        }
                    ]
        )
        overlay.visible = False
        page.update()
           
        def extract_message(response):
            message = ""
            return response.content[0].text.replace("```html", "").replace("```", "")
        
        html = extract_message(response) 
        if os.path.exists(OUTPUT_FILE): 
            os.remove(OUTPUT_FILE)      
        with open(OUTPUT_FILE, "w") as f:
            f.write(html)
        
        
        file_path = os.path.abspath(OUTPUT_FILE)
        # wv = ft.webview.WebView(
        #     url=f"file://{file_path}",  # 
        #     width=800,
        #     height=600
        # )
        # page.remove(fileimage_save)
        # print(f"File path: {file_path}")
        # print(f"File exists: {os.path.exists(file_path)}")
        # page.launch_url(f"file://{file_path}")
        webbrowser.open(f"file://{file_path}")
    
    # Correction details
    correction_details = ft.TextField(hint_text="Enter corrections", multiline=True, width=600,)
    
    def apply_corrections(e):  
        file_path = os.path.abspath(OUTPUT_FILE)
        # set html_cotnent form file_path
        html_content = ""
        with open(file_path, "r") as f:  
            html_content = f.read()
        
        overlay.visible = True
        page.update()
        response = client.messages.create(
            model=model,
            system="You are a Web Designer and HTML/CSS editor. You can edit the HTML code. Return only the modified HTML and CSS code without any explanation.",
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": html_content,
                        },
                        {
                            "type": "text",
                            "text": f"corrections:{correction_details.value}",
                        },
                        {
                            "type": "text",
                            "text": "Please modify the HTML with about the corrections and return only the updated code.",
                        }
                    ],
                }
            ]
        )
        overlay.visible = False
        page.update()
        
        #print(response.content[0].text)
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        with open(OUTPUT_FILE, "w") as f:
            f.write(response.content[0].text)   
        file_path = os.path.abspath(OUTPUT_FILE)
        webbrowser.open(f"file://{file_path}")
    
    button_row = ft.Row(
    controls=[
            ft.ElevatedButton("Load Image", on_click=load_image),
            ft.ElevatedButton("Generate HTML/CSS", on_click=generate_html_css)
        ],
    )
    page.add(button_row)
    page.add(
        ft.Row([
            ft.Column([correction_details]),
            ft.ElevatedButton("Apply Corrections", on_click=apply_corrections)
        ])
    )
    page.overlay.append(overlay)

if __name__ == "__main__":
    ft.app(target=main)