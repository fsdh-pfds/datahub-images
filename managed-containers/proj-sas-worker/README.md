# Test Docker container
<pre>
docker build -t projsas .
docker tag projsas ghcr.io/ssc-sp/projsas
docker push ghcr.io/ssc-sp/projsas   
# Change the image visibility to public
</pre>