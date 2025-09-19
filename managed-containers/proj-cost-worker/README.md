# Test Docker container

<pre>
docker build -t projcost .
docker tag projcost ghcr.io/ssc-sp/projcost
docker push ghcr.io/ssc-sp/projcost   
# Change the image visibility to public
</pre>
