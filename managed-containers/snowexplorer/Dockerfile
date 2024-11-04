FROM condaforge/mambaforge:latest

EXPOSE 8080

COPY environment.yml /app/environment.yml
COPY SnowExplorer-V5.ipynb /app/SnowExplorer-V5.ipynb

RUN mamba env update -q -n base -f /app/environment.yml 
CMD panel serve --port 8080 --num-threads 10 --unused-session-lifetime 60000 --allow-websocket-origin="*" /app/SnowExplorer-V5.ipynb
