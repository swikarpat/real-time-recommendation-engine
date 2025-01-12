#!/bin/bash

# Build the Docker image for the inference service
docker build -t your-docker-repo/recommendation-inference-service:latest .

# Push the Docker image to your registry (e.g., Docker Hub, ECR)
docker push your-docker-repo/recommendation-inference-service:latest