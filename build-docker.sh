#!/bin/bash
# TimeCraft Docker Build Script
# This script rebuilds the Docker image with the latest code changes

echo "Building TimeCraft Docker image with latest changes..."
echo "Note: This will include any UI updates made to scenario-timeseries.html"

# Remove any existing image to force a complete rebuild
echo "Removing existing TimeCraft image (if any)..."
docker rmi timecraft:latest 2>/dev/null || true

# Build the new image
echo "Building new TimeCraft image..."
docker build -t timecraft:latest .

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo "To run the container: docker run -p 8080:8080 timecraft:latest"
else
    echo "❌ Docker build failed!"
    exit 1
fi