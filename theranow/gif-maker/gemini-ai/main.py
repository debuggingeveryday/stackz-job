from kivy.config import Config
import io
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.app import App
from kivy.uix.image import Image as KivyImage
from PIL import ImageGrab
from icecream import ic

# 1 enables exit on escape, 0 disables it
Config.set("kivy", "exit_on_escape", "1")


class GifMakerApp(App):
    def build(self):
        self.pil_frames = []
        self.frame_index = 0
        self.main_layout = BoxLayout(orientation="vertical")
        self.image_layout = BoxLayout(orientation="horizontal")
        self.frame_layout = BoxLayout(orientation="vertical")

        self.add_frame_button = Button(text="Add frame", size_hint=(1, None), height=50)
        self.paste_image_button = Button(
            text="Paste image", size_hint=(1, None), height=50
        )
        self.export_gif_button = Button(
            text="Export GIF", size_hint=(1, None), height=50
        )

        self.export_gif_button.bind(on_press=self.export_to_gif)
        self.add_frame_button.bind(on_press=self.on_add_frame)

        self.main_layout.add_widget(self.image_layout)
        self.main_layout.add_widget(self.add_frame_button)
        self.main_layout.add_widget(self.export_gif_button)

        self.on_add_frame(None)

        return self.main_layout

    def on_add_frame(self, instance):
        frame_layout = BoxLayout(orientation="vertical")
        option_layout = BoxLayout(
            orientation="horizontal", size_hint=(1, None), height=30
        )
        add_frame_button = Button(text="Paste", size_hint=(1, None), height=30)
        delete_frame_button = Button(text="Delete", size_hint=(1, None), height=30)

        add_frame_button.bind(on_press=self.paste_image)
        delete_frame_button.bind(on_press=self.delete_image)

        option_layout.add_widget(add_frame_button)
        option_layout.add_widget(delete_frame_button)
        frame_layout.add_widget(option_layout)
        self.image_layout.add_widget(frame_layout)

        return True

    def delete_image(self, instance):
        frame_layout = instance.parent.parent

        self.main_layout.remove_widget(frame_layout)
        return True

    def paste_image(self, instance):
        try:
            frame_layout = instance.parent.parent
            last_kivy_img = frame_layout.children

            if len(last_kivy_img) > 1:
                return True

            # frame_layout.remove_widget(last_kivy_img)

            kivy_img = KivyImage(source="")
            pil_img = ImageGrab.grabclipboard()

            # Check if the clipboard actually contains an image
            if pil_img is None:
                print("No image found in clipboard!")
                return

            self.pil_frames.append(pil_img)

            # 2. Save the PIL image into an in-memory byte buffer
            byte_io = io.BytesIO()
            pil_img.save(byte_io, format="PNG")
            byte_io.seek(0)

            # 3. Load bytes into Kivy's CoreImage and extract the texture
            core_image = CoreImage(byte_io, ext="png")

            # 4. Assign the texture directly to the Kivy Image widget
            kivy_img.texture = core_image.texture
            kivy_img.fit_mode = "fill"
            kivy_img.size_hint = (1, 1)

            frame_layout.add_widget(kivy_img, index=2)

            print("Image successfully pasted!")
        except Exception as e:
            print(f"Error pasting image: {e}")

        return True

    # 3. Create a new button/method to compile and save the final GIF
    def export_to_gif(self, instance):
        if not self.pil_frames:
            print("No frames to export!")
            return

        try:
            self.pil_frames[0].save(
                "output.gif",
                save_all=True,
                append_images=self.pil_frames[1:],
                duration=1500,  # 300ms per frame
                loop=0,
            )
            print("GIF successfully exported to output.gif!")
        except Exception as e:
            print(f"Failed to export GIF: {e}")


if __name__ == "__main__":
    GifMakerApp().run()
