FROM condaforge/mambaforge:latest

EXPOSE 8080

COPY environment.yml /app/environment.yml
COPY SnowExplorer-V5.ipynb /app/SnowExplorer-V5.ipynb
COPY score_snw_station_diff_alti_200_HRDPS_CaPA01_CaPA02_period_20191001_20220629.nc /data/score_snw_station_diff_alti_200_HRDPS_CaPA01_CaPA02_period_20191001_20220629.nc
COPY series_snw_station_diff_alti_200_HRDPS_CaPA01_CaPA02_period_20191001_20220629.nc /data/series_snw_station_diff_alti_200_HRDPS_CaPA01_CaPA02_period_20191001_20220629.nc

RUN mamba env update -q -n base -f /app/environment.yml 
CMD panel serve --autoreload --port 8080 --num-threads 10 --unused-session-lifetime 60000 --allow-websocket-origin="*" /app/SnowExplorer-V5.ipynb
