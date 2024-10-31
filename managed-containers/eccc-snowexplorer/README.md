# Docker 

## Build and run locally

### Build

```bash
docker build . -f ./Dockerfile -t snowexplorer-fsdh:latest
```

### Run

```bash
docker run -v /mnt/e/AI_Prcp_test1/:/data -t snowexplorer-fsdh:latest
``` 
