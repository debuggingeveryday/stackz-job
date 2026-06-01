FROM python:3.10-slim

# Avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libsdl2-mixer-dev \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libpng-dev \
    libjpeg-dev \
    libmtdev-dev \
    xclip \
    bash \
    git \
    make \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python packages
RUN pip install --upgrade pip \
    && pip install kivy icecream pyinstaller pillow

# Kivy environment variables
ENV KIVY_WINDOW=sdl2
ENV KIVY_IMAGE=sdl2

WORKDIR /app

CMD ["bash"]
