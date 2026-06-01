docker build -t kivy . --no-cache

xhost +local:docker

docker run -it --rm -e DISPLAY=$DISPLAY --name kivy -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd):/app kivy /bin/bash 

pyinstaller --onefile --noconsole --name stackz main.py
