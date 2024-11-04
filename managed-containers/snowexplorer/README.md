# SnowExplorer Docker Setup

This repository has everything you need to build the SnowExplorer dashboard, which is a Jupyter Notebook web app. It helps you explore geospatial data using tools like Panel, GeoViews, Xarray, and more. The project uses Docker to make sure the environment is easy to set up and use.

## Contents

- **Dockerfile**: A file for setting up the Conda environment and running the app.
- **environment.yml**: Defines the Conda environment and all the dependencies.
- **snowexplorer.ipynb**: The Jupyter Notebook with the main application.

## What You Need

To use this project, you need:

- Docker installed on your computer.
- A basic understanding of Docker commands.

## Getting Started

To build and run the Docker image for SnowExplorer:

1. **Clone the Repository**:

   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Build the Docker Image**:

   ```sh
   docker build -t snowexplorer .
   ```

3. **Run the Container**:

   Before running the container, make sure to copy your data files into the `data` directory and set the appropriate data paths as environment variables.

   ```sh
   docker run -p 8080:8080 \
     -e SCORE_FILE=/data/score_snw_station_diff_alti.nc \
     -e SERIES_FILE=/data/series_snw_station_diff_alti.nc \
     -v ./data:/data \
     -v ./SnowExplorer-V5.ipynb:/snowexplorer.ipynb \
     snowexplorer
   ```

## Setting Up the Environment

The `environment.yml` file sets up the Conda environment called `snowexplorer`. It includes all the important tools like `panel`, `dask`, `xarray`, and `bokeh` that are needed for the app.

## About the Application

The main application (`snowexplorer.ipynb`) lets you visualize geospatial data interactively, using:

- **GeoViews** and **Holoviews** for making interactive maps.
- **Panel** to serve the Jupyter Notebook as a web app.
- **Dask** and **Xarray** for handling large datasets.

## Dockerfile Details

The Dockerfile has two main parts:

- **Base Stage**: Uses `condaforge/miniforge3` to set up a Conda environment and install all needed tools from `environment.yml`.
- **Final Stage**: Uses a lightweight Python image from Chainguard to create the environment for running the web server.

### Important Dockerfile Parts

- **Multi-Stage Build**: Keeps the image small by separating the setup and runtime stages.
- **Non-Root User**: The container runs as a non-root user (`nonroot`) for better security.
- **Health Check**: Checks if the service is running correctly by using the `/health` endpoint.

## Customizing the Application

You can adjust the default settings for the Panel server by changing the `CMD` directive in the Dockerfile. For example, you can change the number of processes or threads:

```dockerfile
CMD ["--num-procs=2", "--num-threads=5"]
```

This lets you tweak how the server runs to fit your needs.

## Using the Image from GitHub Container Registry

_Placeholder: Instructions on how to pull and use the Docker image from the GitHub Container Registry will be added here._

## Running with Docker Compose

You can use Docker Compose to build and run the SnowExplorer container with all the needed volume mounts and environment variables. Here's an example `docker-compose.yml` file:

```yaml
version: "3.3" # or a different version that suits your Docker environment

services:
  panel:
    build:
      context: .
      dockerfile: Dockerfile
    restart: always
    ports:
      - "8080:8080"
    environment:
      - SCORE_FILE=/data/score_snw_station_diff_alti.nc
      - SERIES_FILE=/data/series_snw_station_diff_alti.nc
    volumes:
      # FSDH Config
      - ./data:/data
      - ./SnowExplorer-V5.ipynb:/snowexplorer.ipynb
```

To run the application using Docker Compose:

```sh
docker-compose build --progress=plain

docker-compose up
```

The first command will build the image, and the second will run the container based on what's in the `docker-compose.yml` file.
