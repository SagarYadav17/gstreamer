# Project Name

This project uses GStreamer for media processing and PyCairo for graphics. It is containerized using Docker.

## Docker Image

The Docker image is based on Ubuntu and includes Python 3, GStreamer, and PyCairo.

## Building the Docker Image

To build the Docker image, navigate to the directory containing the Dockerfile and run the following command:

```bash
docker build -t my-image .
```

Replace `my-image` with the desired name for the Docker image.

Running the Docker Image
To run the Docker image, use the following command:

```bash
docker run -it --rm my-image
```

Replace `my-image` with the name of the Docker image.
