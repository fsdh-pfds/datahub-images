# Get the JSON array of Dockerfiles to build from the previous step
dockerfiles_json='${{ steps.generate_dockerfile_list.outputs.dockerfiles_to_build }}'
# Convert JSON array to a bash array
mapfile -t dockerfiles_list < <(echo "$dockerfiles_json" | jq -r '.[]')

mkdir -p trivy-results

echo "Dockerfile files to process: ${dockerfiles_list[*]}"

# Iterate through each Dockerfile path
for dockerfile in "${dockerfiles_list[@]}"; do
# Extract the package name from the directory containing the Dockerfile and convert to lowercase
package_name="$(basename $(dirname $dockerfile) | tr '[:upper:]' '[:lower:]')"

# Define the image name with the :latest tag
image_name="$package_name:latest"
repo_path="ghcr.io/${{ github.repository_owner }}/$image_name"

echo "Building Docker image: $image_name from $dockerfile"
echo $repo_path 

# Build the Docker image using Docker Buildx with --no-cache to ensure fresh layers
docker buildx build --load --no-cache -t "$repo_path" -f "$dockerfile" "$(dirname $dockerfile)"

docker push "$repo_path"

echo "Scanning $image_name..."
trivy image --severity CRITICAL,HIGH --format sarif --output "trivy-results/${package_name}.sarif" "$repo_path"

done