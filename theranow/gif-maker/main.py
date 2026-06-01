import io
import glob
from PIL import Image as PILImage
from PIL import ImageGrab
from PIL import ImageSequence
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image as KivyImage
from kivy.core.image import Image as CoreImage
from kivy.graphics import Rectangle, Color
from kivy.uix.button import Button
from icecream import ic
from kivy.config import Config

# 1 enables exit on escape, 0 disables it
Config.set("kivy", "exit_on_escape", "1")


class GifMakerApp(App):
    def build(self):
        self.crop_box = None
        self.is_crop_mode = False
        self.layout = FloatLayout()
        self.option_layout = BoxLayout(orientation="horizontal")

        self.pil_img = None
        self.frame_index = 1

        # Image widget to display the pasted image
        self.kivy_img = KivyImage(source="")
        self.layout.add_widget(self.kivy_img)

        # Trigger button
        self.paste_button = Button(
            text="Paste Image from Clipboard", size_hint=(1, None), height=50
        )

        self.crop_button = Button(
            text=f"Crop Frame {self.frame_index}", size_hint=(1, None), height=50
        )

        self.cancel_crop_button = Button(text=f"Cancel", size_hint=(1, None), height=50)
        self.done_button = Button(text=f"Done", size_hint=(1, None), height=50)

        self.option_layout.add_widget(self.crop_button)
        self.option_layout.add_widget(self.cancel_crop_button)
        self.option_layout.add_widget(self.done_button)

        self.paste_button.bind(on_press=self.paste_image)
        self.crop_button.bind(on_press=self.on_crop)
        self.cancel_crop_button.bind(on_press=self.on_cancel_crop)
        self.done_button.bind(on_press=self.on_done)
        self.layout.add_widget(self.paste_button)

        # 3. Bind touch events for the selection tool
        self.kivy_img.bind(on_touch_down=self.on_touch_down)
        self.kivy_img.bind(on_touch_move=self.on_touch_move)
        self.kivy_img.bind(on_touch_up=self.on_touch_up)

        # Selection variables
        self.start_pos = None
        self.current_rect = None
        self.crop_rect = None

        return self.layout

    def on_done(self, instance):
        frames = [PILImage.open(f) for f in sorted(glob.glob("frame_*.png"))]
        frame_one = frames[0]
        frame_one.save(
            "animation.gif",
            format="GIF",
            append_images=frames[1:],
            save_all=True,
            duration=1500,
            loop=0,
        )
        print("Done")

        return True

    def on_crop(self, instance):
        # 4. Crop using Pillow and save the selection
        cropped_img = self.pil_img.crop(self.crop_box)
        cropped_img.save(f"frame_{self.frame_index}.png")
        self.frame_index += 1
        self.layout.remove_widget(self.option_layout)
        self.is_crop_mode = True

    def paste_image(self, instance):
        try:
            self.is_crop_mode = True

            # 1. Grab the image data from the system clipboard using Pillow
            self.pil_img = ImageGrab.grabclipboard()

            # Check if the clipboard actually contains an image
            if self.pil_img is None:
                print("No image found in clipboard!")
                return

            # 2. Save the PIL image into an in-memory byte buffer
            byte_io = io.BytesIO()
            self.pil_img.save(byte_io, format="PNG")
            byte_io.seek(0)

            # 3. Load bytes into Kivy's CoreImage and extract the texture
            core_image = CoreImage(byte_io, ext="png")

            # 4. Assign the texture directly to the Kivy Image widget
            self.kivy_img.texture = core_image.texture
            self.kivy_img.fit_mode = "fill"
            self.kivy_img.size_hint = (1, 1)

            self.layout.remove_widget(self.paste_button)

            print("Image successfully pasted!")

        except Exception as e:
            print(f"Error pasting image: {e}")

    def on_touch_down(self, instance, touch):
        if self.is_crop_mode == False:
            return

        if instance.collide_point(*touch.pos):
            # Record starting click position
            self.start_pos = touch.pos

            # Create a visual rectangle overlay
            with instance.canvas:
                Color(1, 0, 0, 0.5)  # Red, 50% transparent
                self.current_rect = Rectangle(pos=touch.pos, size=(0, 0))
            return True

    def on_touch_move(self, instance, touch):
        if self.is_crop_mode == False:
            return

        if self.start_pos and self.current_rect:
            # Calculate the width and height of the selection
            width = touch.x - self.start_pos[0]
            height = touch.y - self.start_pos[1]

            # Normalize size (handles dragging in reverse directions)
            abs_width = abs(width)
            abs_height = abs(height)
            abs_x = min(self.start_pos[0], touch.x)
            abs_y = min(self.start_pos[1], touch.y)

            self.current_rect.pos = (abs_x, abs_y)
            self.current_rect.size = (abs_width, abs_height)

            return True

    def on_cancel_crop(self, instance):
        self.crop_box = None
        self.current_rect = None
        self.is_crop_mode = True
        self.layout.remove_widget(self.option_layout)
        return True

    def on_touch_up(self, instance, touch):
        if self.crop_rect:
            instance.canvas.remove(self.crop_rect)
            self.crop_rect = None

        if self.start_pos and self.current_rect:
            # 1. Remove the selection box from Kivy canvas
            instance.canvas.remove(self.current_rect)

            # 2. Get the bounding box in UI coordinates
            x1, y1 = self.start_pos
            x2, y2 = touch.pos

            ui_x = min(x1, x2)
            ui_y = min(y1, y2)
            ui_w = abs(x2 - x1)
            ui_h = abs(y2 - y1)

            # Ignore tiny accidental clicks
            if ui_w < 10 or ui_h < 10:
                return True

            # 3. Convert UI coordinates to Pillow image coordinates
            # (Kivy has the origin at bottom-left, PIL has it at top-left)
            img_w, img_h = self.pil_img.size

            # Get ratio of UI size to Kivy displayed size
            scale_x = img_w / instance.width
            scale_y = img_h / (instance.height)

            # Calculate PIL crop box
            pil_x1 = int(ui_x * scale_x)
            pil_y1 = int((instance.height - (ui_y + ui_h)) * scale_y)
            pil_x2 = int((ui_x + ui_w) * scale_x)
            pil_y2 = int((instance.height - ui_y) * scale_y)

            self.crop_box = (pil_x1, pil_y1, pil_x2, pil_y2)

            with instance.canvas:
                Color(0, 1, 0, 0.5)  # Red, 50% transparent
                self.crop_rect = Rectangle(pos=self.start_pos, size=(x2 - x1, y2 - y1))

            self.layout.remove_widget(self.paste_button)

            self.crop_button.text = f"Crop Frame {self.frame_index}"

            self.layout.add_widget(self.option_layout)

            self.start_pos = None
            self.is_crop_mode = False

            return True


if __name__ == "__main__":
    GifMakerApp().run()
