import os
import pandas as pd
import json
from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import PredictionServiceClient
from google.protobuf.struct_pb2 import Value
from google.protobuf import json_format
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables (set in the bash script)
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = os.environ.get("GCP_REGION")
EMBEDDING_ENDPOINT_ID = os.environ.get("EMBEDDING_ENDPOINT_ID")
CSV_GCS_PATH = os.environ.get("CSV_GCS_PATH")
CSV_COLUMN_NAME = os.environ.get("CSV_COLUMN_NAME")
VS_INPUT_GCS_BUCKET = os.environ.get("VS_INPUT_GCS_BUCKET")

# Initialize Vertex AI SDK
aiplatform.init(project=PROJECT_ID, location=REGION)

# Initialize PredictionServiceClient for calling your embedding model endpoint
embedding_client = PredictionServiceClient(
    client_options={"api_endpoint": f"{REGION}-aiplatform.googleapis.com"}
)
embedding_endpoint_path = embedding_client.endpoint_path(
    project=PROJECT_ID, location=REGION, endpoint=EMBEDDING_ENDPOINT_ID
)

async def _generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generates embeddings for a list of texts using the deployed Vertex AI embedding endpoint.
    """
    if not texts:
        return []

    logger.info(f"Generating embeddings for {len(texts)} texts...")

    # For sentence-transformers/all-MiniLM-L6-v2, the instances are typically just the list of strings
    # The `Value` conversion is for the protobuf structure expected by the API.
    instances_proto = [json_format.ParseDict(text, Value()) for text in texts]

    try:
        response = embedding_client.predict(
            endpoint=embedding_endpoint_path,
            instances=instances_proto
        )
        # Assuming your predictor.py returns a list of lists of floats directly
        embeddings = [json.loads(json_format.MessageToJson(prediction)) for prediction in response.predictions]
        logger.info(f"Generated {len(embeddings)} embeddings.")
        return embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise

async def generate_vector_search_input_data():
    """
    Reads data, generates embeddings, and prepares JSONL for Vertex AI Vector Search.
    """
    logger.info("Starting to prepare Vector Search input data...")

    # 1. Load the dataset
    try:
        df = pd.read_csv('quotes.csv')
        texts = df[CSV_COLUMN_NAME].dropna().tolist()
    except Exception as e:
        logger.error(f"Error reading CSV : {e}")
        raise

    if not texts:
        logger.warning("No texts found in CSV to process.")
        return

    # 2. Generate embeddings in batches
    batch_size = 10 # Adjust based on your model's API limits and concurrency
    all_embeddings_data = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        batch_embeddings = await _generate_embeddings_batch(batch_texts)

        if not batch_embeddings:
            logger.warning(f"No embeddings returned for batch starting at index {i}. Skipping.")
            continue

        for j, embedding in enumerate(batch_embeddings):
            original_text = batch_texts[j]
            # Create a unique ID for each document/chunk. Use something stable if re-running.
            doc_id = f"doc_{i+j}" # Simple sequential ID

            all_embeddings_data.append({
                "id": doc_id,
                "embedding": embedding,
                # Optional: Add metadata for filtering/retrieval later
                "metadata": {"original_text": original_text}
            })

    # 3. Write embeddings to a local JSONL file
    local_embedding_file = "embeddings_data.jsonl"
    with open(local_embedding_file, 'w') as f:
        for entry in all_embeddings_data:
            f.write(json.dumps(entry) + '\n')

    logger.info(f"Embeddings saved locally to {local_embedding_file}")
    
    # 4. Upload the JSONL file to GCS
    # The 'gcloud storage cp' command (or gsutil cp) is often more robust for large files/folders
    # We'll call this from the bash script in the next step.
    
    return local_embedding_file # Return the path for the bash script to upload

if __name__ == "__main__":
    # Ensure all required environment variables are set before running
    required_vars = ["GCP_PROJECT_ID", "GCP_REGION", "EMBEDDING_ENDPOINT_ID", 
                     "CSV_GCS_PATH", "CSV_COLUMN_NAME", "VS_INPUT_GCS_BUCKET"]
    if not all(os.environ.get(var) for var in required_vars):
        logger.error("Missing one or more required environment variables. Please set them in your bash script.")
        exit(1)
        
    asyncio.run(generate_vector_search_input_data())