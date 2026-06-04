from kivy.config import Config
import io
import os
from kivy.core.image import Image as CoreImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.app import App
from kivy.uix.image import Image as KivyImage
from PIL import ImageGrab
from PIL import Image as PILImage
from icecream import ic

# 1 enables exit on escape, 0 disables it
Config.set("kivy", "exit_on_escape", "1")


class GifMakerApp(App):
    def build(self):
        self.gifs_dir = "../gifs"
        self.pil_frames = []
        self.frame_index = 0
        self.file_name = ""
        os.makedirs(self.gifs_dir, exist_ok=True)

        self.main_layout = BoxLayout(orientation="vertical")
        self.image_layout = BoxLayout(orientation="horizontal")
        self.frame_layout = BoxLayout(orientation="vertical")

        self.file_name_input = TextInput(
            text="",
            size_hint=(1, None),
            height=50,
            multiline=False,
            hint_text="Enter output GIF name and press Enter",
        )

        self.add_frame_button = Button(text="Add frame", size_hint=(1, None), height=50)
        self.paste_image_button = Button(
            text="Paste image", size_hint=(1, None), height=50
        )
        self.export_gif_button = Button(
            text="Export GIF", size_hint=(1, None), height=50
        )

        self.export_gif_button.bind(on_press=self.export_to_gif)
        self.add_frame_button.bind(on_press=self.on_add_frame)
        self.file_name_input.bind(on_text_validate=self.on_enter)

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

        self.image_layout.remove_widget(frame_layout)
        return True

    def paste_image(self, instance):
        try:
            frame_layout = instance.parent.parent
            last_kivy_img = frame_layout.children

            if len(last_kivy_img) > 1:
                return True

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

    def on_enter(self, instance):
        file_name = instance.text

        if not self.pil_frames:
            print("No frames to export!")
            return

        if self.pil_frames:
            # 2. Find the largest width and largest height among all frames
            max_w = max(img.width for img in self.pil_frames)
            max_h = max(img.height for img in self.pil_frames)
            max_size = (max_w, max_h)

            # 3. Resize/Pad all frames to match the largest size
            # This prevents warping and ensures every frame fits perfectly
            unified_frames = []
            for img in self.pil_frames:
                # Create a black background canvas of the maximum size
                canvas = PILImage.new("RGBA", max_size, (255, 255, 255, 0))

                # Center the original image on the canvas
                x_offset = (max_w - img.width) // 2
                y_offset = (max_h - img.height) // 2
                canvas.paste(img, (x_offset, y_offset))

                # Convert to RGB (required for saving standard GIFs cleanly)
                unified_frames.append(canvas.convert("RGB"))

            # 4. Save the GIF using the unified frames
            frame_one = unified_frames[0]
            frame_one.save(
                f"gifs/{file_name}.gif",
                format="GIF",
                append_images=unified_frames[1:],
                save_all=True,
                duration=1500,
                loop=0,
            )

        self.file_name_input.text = ""

        # try:
        #     self.pil_frames[0].save(
        #         f"{instance.text}.gif",
        #         save_all=True,
        #         append_images=self.pil_frames[1:],
        #         duration=1500,  # 300ms per frame
        #         loop=0,
        #     )
        #     print("GIF successfully exported to output.gif!")
        # except Exception as e:
        #     print(f"Failed to export GIF: {e}")

        self.main_layout.remove_widget(self.file_name_input)
        self.main_layout.add_widget(self.export_gif_button)
        self.main_layout.add_widget(self.add_frame_button)

        return True

    # 3. Create a new button/method to compile and save the final GIF
    def export_to_gif(self, instance):
        self.main_layout.add_widget(self.file_name_input)
        self.main_layout.remove_widget(self.export_gif_button)
        self.main_layout.remove_widget(self.add_frame_button)
        return True


if __name__ == "__main__":
    GifMakerApp().run()
