#!/bin/bash

set -e

export PROJECT_ID="my-web-page-230207" # Replace with your GCP project ID
export REGION="europe-west3" # Choose a region, e.g., us-central1
export REPO_NAME="vertex-ai-models" # Or any name for your Artifact Registry repo
export IMAGE_NAME="all-minilm-l6-v2-predictor"
export IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:latest"

export MODEL_NAME="all-MiniLM-L6-v2-model"
export MODEL_DESCRIPTION="Sentence-Transformers all-MiniLM-L6-v2 model for embeddings"
export ARTIFACT_BUCKET="${PROJECT_ID}-vertex-ai-bucket"
export ARTIFACT_URI="gs://${ARTIFACT_BUCKET}/${MODEL_NAME}"


gcloud services enable artifactregistry.googleapis.com # if not enabled

gcloud artifacts repositories create ${REPO_NAME} \
    --repository-format=docker \
    --location=${REGION} \
    --description="Docker repository for Vertex AI custom models" \
    --async

gcloud auth configure-docker ${REGION}-docker.pkg.dev

docker buildx build --platform linux/amd64 -t ${IMAGE_URI} .
docker push ${IMAGE_URI}

/usr/bin/python3 save_locally.py # Please change this to your python path
gsutil cp -r ./all-MiniLM-L6-v2-model ${ARTIFACT_URI}/
/usr/bin/python3 init_and_deploy.py # Please change this to your python path