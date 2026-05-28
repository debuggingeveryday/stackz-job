from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout


class MainLayout(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        scroll = ScrollView()

        # GRID
        grid = GridLayout(cols=3, spacing=10, padding=10, size_hint_y=None)

        grid.bind(minimum_height=grid.setter("height"))

        data = [
            ["1", "Squat Exercise", "Easy"],
            ["2", "Push Up Exercise", "Medium"],
            ["3", "Lunge Exercise", "Hard"],
        ]

        for row in data:

            for text in row:

                label = Label(
                    text=text,
                    size_hint_y=None,
                    height=40,
                    # IMPORTANT
                    size_hint_x=None,
                    width=250,
                    halign="left",
                    valign="middle",
                )

                # REQUIRED FOR TEXT ALIGNMENT
                label.bind(
                    size=lambda instance, value: setattr(instance, "text_size", value)
                )

                grid.add_widget(label)

        scroll.add_widget(grid)

        self.add_widget(scroll)


class MyApp(App):
    def build(self):
        return MainLayout()


MyApp().run()
