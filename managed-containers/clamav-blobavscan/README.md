# Test Docker container
<pre>
docker build -t blobscaneg .
docker tag blobscaneg ghcr.io/ssc-sp/blobscaneg
docker push ghcr.io/ssc-sp/blobscaneg   
# Change the image visibility to public
</pre>