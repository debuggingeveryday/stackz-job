from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.core.clipboard import Clipboard
import csv
import json
from icecream import ic


class FilePicker(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        self.label = Label(text="No file selected", size_hint=(1, 0.1))

        # PAGE 1
        self.file_page = BoxLayout(orientation="vertical")

        self.filechooser = FileChooserListView(path=".", filters=["*.csv"])
        self.selected = ""

        self.button = Button(text="Select File", size_hint=(1, 0.1))

        self.button.bind(on_press=self.select_file)

        self.add_widget(self.label)
        self.add_widget(self.filechooser)
        self.add_widget(self.button)

        self.add_widget(self.file_page)

        self.list_page = BoxLayout(orientation="vertical")
        self.title = Label(text="CSV Content", size_hint=(1, 0.1))
        self.scroll = ScrollView()
        self.grid = GridLayout(
            cols=5,
            row_force_default=True,
            row_default_height=40,
            spacing=10,
            padding=[10, 10, 10, 10],
            size_hint_y=None,
        )
        self.data = []

    def select_file(self, instance):
        self.selected = self.filechooser.selection

        headers = [
            "Exercise ID",
            "Exercise Name",
            "Duplicate Check",
            "Position",
            "Prop Used",
            "Main Body Part",
            "Main Joint",
            "Main Muscle",
            "Category",
            "Movement Type",
            "Difficulty",
            "Rehab Phase",
            "Conditions",
            "Keywords",
            "Description",
            "GIF Path",
            "Created on",
            "Created by",
            "Audit Status",
            "Audit Done on",
            "Audit Outcome",
            "Comments",
            "Correction Status",
            "Correction done on",
            "Step1 Prompt",
            "Step2 Prompt",
            "Step3 Prompt",
        ]

        keys_to_remove = [
            "GIF Path",
            "Created on",
            "Created by",
            "Audit Status",
            "Audit Done on",
            "Correction Status",
            "Correction done on",
            "Audit Outcome",
            "Comments",
        ]

        if not self.selected:
            self.label.text = "No file selected"
            return

        filepath = self.selected[0]

        self.label.text = f"Selected:\n{filepath}"

        # READ CSV FILE
        with open(filepath, "r", newline="") as file:
            reader = csv.reader(file)

            for row in reader:
                item = {}
                is_correction_needed = False
                important_correction_value = ""

                for i, header in enumerate(headers):
                    if not i < len(row):
                        item[header] = ""
                        break

                    if header == "Audit Outcome" and row[i] == "Correction need":
                        is_correction_needed = True
                        pass

                    if header == "Comments" and is_correction_needed == True:
                        important_correction_value = row[i]
                        pass

                    item[header] = row[i]

                if is_correction_needed == True:
                    item["Important Correction"] = important_correction_value
                    is_correction_needed = False

                for key in keys_to_remove:
                    item.pop(key, None)

                self.data.append(item)

        # ic(self.data)

        # CHANGE PAGE
        self.clear_widgets()
        self.list_prompt(instance)

    def list_prompt(self, instance):
        self.grid.clear_widgets()

        # ADD ROWS
        for index, row in enumerate(self.data):
            row_text = row["Exercise ID"]

            row_label = Label(
                text=row_text,
                size_hint_y=None,
                height=40,
                width=150,
                halign="left",
                valign="middle",
                size_hint_x=None,
            )

            self.grid.add_widget(row_label)

            row_text = row["Exercise Name"]

            row_label = Label(
                text=row_text,
                size_hint_y=None,
                height=40,
                size_hint_x=1,
                width=1000,
                halign="left",
                valign="middle",
            )

            self.grid.add_widget(row_label)

            my_button = Button(
                text="Copy Title", size_hint_x=None, height=40, width=100
            )

            my_button.bind(
                on_press=lambda instance, idx=index: self.copy_title_function(
                    instance, self.data[idx]["Exercise Name"]
                )
            )

            self.grid.add_widget(my_button)

            my_button = Button(
                text="Copy Prompt", size_hint_x=None, height=40, width=100
            )

            # BUTTON EVENT
            my_button.bind(
                on_press=lambda instance, idx=index: self.copy_prompt_function(
                    instance, self.data[idx]
                )
            )

            # ADD TO LAYOUT
            self.grid.add_widget(my_button)

            my_button = Button(text="Remove", size_hint_x=None, height=40, width=100)

            # BUTTON EVENT
            my_button.bind(
                on_press=lambda instance, idx=index: self.remove_function(instance, idx)
            )

            # ADD TO LAYOUT
            self.grid.add_widget(my_button)

            if self.grid.parent is None:
                self.scroll.add_widget(self.grid)

            if self.scroll.parent is None:
                self.list_page.add_widget(self.title)
                self.list_page.add_widget(self.scroll)

            if self.list_page.parent is None:
                self.add_widget(self.list_page)

            # print(json.dumps(data, indent=4))

    def copy_title_function(self, instance, value):
        Clipboard.copy(value)

    def copy_prompt_function(self, instance, value):
        Clipboard.copy(str(value))

    def remove_function(self, instance, index):
        # remove data
        self.data.pop(index)

        # clear old widgets
        self.grid.clear_widgets()

        # rebuild list
        self.list_prompt(instance)

        print(f"Removed row {index}")


class MyApp(App):
    def build(self):
        return FilePicker()


MyApp().run()
