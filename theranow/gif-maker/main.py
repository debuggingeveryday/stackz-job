from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label


class GifMaker(BoxLayout):
    pass


class MyApp(App):
    def build(self):
        return GifMaker()


MyApp().run()
