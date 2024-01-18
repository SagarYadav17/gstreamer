# Use Ubuntu as base image
FROM ubuntu:latest

# Update package list
RUN apt-get update

# Install necessary packages
RUN apt-get install -y --fix-missing \
    python3-pip \
    python3-venv \
    python3-gi \
    libgirepository1.0-dev \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    gstreamer1.0-x \
    gstreamer1.0-alsa \
    gstreamer1.0-gl \
    gstreamer1.0-gtk3 \
    gstreamer1.0-qt5 \
    gstreamer1.0-pulseaudio \
    gir1.2-gstreamer-1.0 \
    libcairo2-dev \
    pkg-config \
    python3-dev

# Set environment variables
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
ENV GI_TYPELIB_PATH=/usr/lib/x86_64-linux-gnu/girepository-1.0

# Copy your application to the Docker image
COPY . /app

# Set the working directory
WORKDIR /app

# Create a virtual environment and activate it
RUN python3 -m venv venv
RUN . venv/bin/activate

# Install Python dependencies
RUN venv/bin/pip install --upgrade pip
RUN venv/bin/pip install -r requirements.txt

# Run your application
CMD [ "venv/bin/python3", "stream.py" ]
