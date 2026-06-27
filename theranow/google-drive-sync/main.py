import time
from threading import Timer
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from PIL import Image
from icecream import ic
import subprocess
import configparser

# -- Google Drive API -- #

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# Initialize the parser
config = configparser.ConfigParser()

file_path = Path("config.ini")

if not file_path.is_file():
    raise FileNotFoundError("Config file is missing")

config.read("config.ini")

gauth = GoogleAuth()
gauth.LocalWebserverAuth()

drive = GoogleDrive(gauth)

# Specify the target directory path you want to monitor
DIRECTORY_TO_WATCH = config["settings"]["directory_to_watch"]
GOOGLE_DRIVE_DIRECTORY_ID = config["google-drive"]["google_drive_directory_id"]


def run_once(f):
    def wrapper(*args, **kwargs):
        try:
            event_type, file_path = args

            if event_type == "DELETED":
                wrapper.last_file_path = ""

            file_size = os.path.getsize(file_path)

            if (
                not wrapper.last_event_type == event_type
                and wrapper.last_file_path != file_path
            ):
                wrapper.last_file_size = 0
                wrapper.last_event_type = event_type
                wrapper.last_file_path = file_path

                return f(*args, **kwargs)

            wrapper.last_file_size = file_size

        except Exception as e:
            print(f"An error occurred: {e}.")

    wrapper.last_file_size = 0
    wrapper.last_event_type = ""
    wrapper.last_file_path = ""
    return wrapper


def on_upload(file_path):
    try:
        print("Execute process file for upload to google drive")
        file_name = Path(file_path).stem
        file_drive = drive.CreateFile(
            {
                "title": f"{file_name}.gif",
                "mimeType": "image/gif",
                "parents": [{"id": GOOGLE_DRIVE_DIRECTORY_ID}],
            }
        )

        # Read local file content and upload
        file_drive.SetContentFile(file_path)
        file_drive.Upload()

    except Exception as e:
        print(f"{e}")

    finally:
        print("File uploaded successfully to shared folder!")
        time.sleep(7)
        subprocess.run(["notify-send", "-t", "5000", "Gif uploaded is now toggable"])
        print("Now you can tag to google drive")


# Define your custom actions / functions here
@run_once
def my_trigger_function(event_type, file_path):
    timer_id = Timer(2.0, on_upload, args=[file_path])
    timer_id.start()


def is_gif(file_path):
    try:
        with Image.open(file_path) as img:
            # Returns 'GIF' if the file is a valid GIF
            return img.format == "GIF"
    except (IOError, SyntaxError):
        # Triggered if the file is corrupt or not an image
        return False


class DirectoryWatcherHandler(FileSystemEventHandler):
    """Subclassing FileSystemEventHandler to map OS events to Python functions."""

    def on_created(self, event):
        if not event.is_directory:
            my_trigger_function("CREATED", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            my_trigger_function("MODIFIED", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            my_trigger_function("DELETED", event.src_path)


if __name__ == "__main__":
    # Initialize the handler and the observer daemon
    event_handler = DirectoryWatcherHandler()
    observer = Observer()

    # Schedule the observer
    # Set recursive=True if you want to monitor subdirectories as well
    observer.schedule(event_handler, path=DIRECTORY_TO_WATCH, recursive=False)

    print(f"Starting to watch: {DIRECTORY_TO_WATCH}")
    observer.start()

    try:
        # Keep the main thread alive so the background observer thread can run
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping watcher...")
        observer.stop()

    observer.join()
