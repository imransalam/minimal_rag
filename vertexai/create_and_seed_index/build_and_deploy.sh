#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration Variables (REPLACE THESE) ---
export GCP_PROJECT_ID="my-web-page-230207"
export GCP_REGION="europe-west3"

# GCS Bucket for raw data (your CSV)
export RAW_DATA_GCS_BUCKET="gs://${GCP_PROJECT_ID}-raw-data-bucket"
# GCS Bucket for Vector Search input (JSONL files with embeddings)
export VS_INPUT_GCS_BUCKET="gs://${GCP_PROJECT_ID}-vector-search-input"

# Your deployed Sentence-Transformers embedding model endpoint ID
# Get this from Vertex AI Endpoints, it's a long number string
export EMBEDDING_ENDPOINT_ID="REPLACE_WITH_YOUR_EMBEDDING_MODEL_ENDPOINT_ID"

# Vertex AI Vector Search Index and Endpoint display names
export VS_INDEX_DISPLAY_NAME="my-rag-document-index"
export VS_ENDPOINT_DISPLAY_NAME="my-rag-index-endpoint"

# Input CSV file settings
export CSV_GCS_PATH="${RAW_DATA_GCS_BUCKET}/quotes.csv" # Path to your quotes.csv in GCS
export CSV_COLUMN_NAME="quote" # Column in your CSV containing text to embed

# Other Vector Search parameters
export EMBEDDING_DIMENSION=384 # all-MiniLM-L6-v2 outputs 384-dimensional embeddings
export VS_DISTANCE_MEASURE_TYPE="DOT_PRODUCT_DISTANCE"
export VS_APPROX_NEIGHBORS_COUNT=10
export VS_LEAF_NODES_TO_SEARCH_PERCENT=20

echo "--- Starting Vertex AI Vector Search Deployment ---"
echo "Project ID: ${GCP_PROJECT_ID}"
echo "Region: ${GCP_REGION}"
echo "Embedding Endpoint ID: ${EMBEDDING_ENDPOINT_ID}"
echo "Vector Search Index Display Name: ${VS_INDEX_DISPLAY_NAME}"
echo "Vector Search Endpoint Display Name: ${VS_ENDPOINT_DISPLAY_NAME}"
echo "-------------------------------------------------"

# --- Step 0: Create GCS buckets if they don't exist ---
echo "--- Checking/Creating GCS buckets ---"
gsutil ls "${RAW_DATA_GCS_BUCKET}" || gsutil mb -l "${GCP_REGION}" "${RAW_DATA_GCS_BUCKET}"
gsutil ls "${VS_INPUT_GCS_BUCKET}" || gsutil mb -l "${GCP_REGION}" "${VS_INPUT_GCS_BUCKET}"
echo "GCS buckets checked/created."

# --- Upload your CSV if not already in GCS ---
echo "--- Uploading CSV to GCS (if not already there) ---"
if [ ! -f "quotes.csv" ]; then
  echo "Error: quotes.csv not found. Please ensure your CSV is in the data/ folder."
  exit 1
fi
gsutil cp "quotes.csv" "${CSV_GCS_PATH}"
echo "CSV uploaded to ${CSV_GCS_PATH}"

# --- Step 1: Generate Embeddings and Prepare Data (Python) ---
echo "--- Step 1: Generating Embeddings and Preparing JSONL data (Python) ---"
/usr/bin/python3 generate_vs_data.py # Change to your python path
echo "Embeddings generation and JSONL preparation complete."

# Check if the python script created the file
if [ ! -f "embeddings_data.jsonl" ]; then
    echo "Error: embeddings_data.jsonl not created by Python script. Exiting."
    exit 1
fi

# --- Step 2: Upload Embeddings to GCS (Bash) ---
echo "--- Step 2: Uploading Embeddings to GCS (Bash) ---"
export CURRENT_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
export VS_DATA_GCS_URI="${VS_INPUT_GCS_BUCKET}/data/${VS_INDEX_DISPLAY_NAME}/${CURRENT_TIMESTAMP}/"

gsutil cp embeddings_data.jsonl "${VS_DATA_GCS_URI}"
echo "Embeddings uploaded to: ${VS_DATA_GCS_URI}"

# --- Step 3: Create/Update Vertex AI Vector Search Index (Python) ---
echo "--- Step 3: Creating/Updating Vertex AI Vector Search Index (Python) ---"
/usr/bin/python3 manage_vs_index.py # Change to your python path
echo "Vertex AI Vector Search Index management complete."

# --- Step 4: Create/Deploy Vertex AI Vector Search Index Endpoint (Python) ---
echo "--- Step 4: Creating/Deploying Vertex AI Vector Search Index Endpoint (Python) ---"
/usr/bin/python3 manage_vs_endpoint.py # Change to your python path
echo "Vertex AI Vector Search Endpoint management complete."

echo "--- Deployment Finished ---"
echo "You can now retrieve the endpoint ID from vs_endpoint_id.txt and use it in your FastAPI app."