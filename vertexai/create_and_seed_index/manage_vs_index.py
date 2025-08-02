import os
from google.cloud import aiplatform
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = os.environ.get("GCP_REGION")
VS_INDEX_DISPLAY_NAME = os.environ.get("VS_INDEX_DISPLAY_NAME")
VS_DATA_GCS_URI = os.environ.get("VS_DATA_GCS_URI")
EMBEDDING_DIMENSION = int(os.environ.get("EMBEDDING_DIMENSION"))
VS_DISTANCE_MEASURE_TYPE = os.environ.get("VS_DISTANCE_MEASURE_TYPE")
VS_APPROX_NEIGHBORS_COUNT = int(os.environ.get("VS_APPROX_NEIGHBORS_COUNT"))
VS_LEAF_NODES_TO_SEARCH_PERCENT = int(os.environ.get("VS_LEAF_NODES_TO_SEARCH_PERCENT"))


aiplatform.init(project=PROJECT_ID, location=REGION)

def manage_vector_search_index():
    logger.info("Starting to manage Vertex AI Vector Search index...")

    # Find existing index by display name
    index = None
    try:
        existing_indexes = aiplatform.MatchingEngineIndex.list(filter=f'display_name="{VS_INDEX_DISPLAY_NAME}"')
        if existing_indexes:
            index = existing_indexes[0]
            logger.info(f"Found existing Vector Search Index: {index.resource_name}. Updating it.")
            # Updating an existing index with new data
            # Use is_complete_overwrite=True for full replacement of the index content
            # This is generally recommended for batch updates from scratch.
            operation = index.update_embeddings(
                contents_delta_uri=VS_DATA_GCS_URI, # New data to ingest
                is_complete_overwrite=True
            )
            logger.info(f"Vector Search Index {index.resource_name} update initiated. Operation: {operation.name}")
            operation.wait() # Wait for the update operation to complete
            logger.info(f"Vector Search Index {index.resource_name} updated successfully.")
        else:
            logger.info("No existing Vector Search Index found. Creating a new one.")
            # Create the Vector Search Index
            index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
                display_name=VS_INDEX_DISPLAY_NAME,
                contents_delta_uri=VS_DATA_GCS_URI, # Path to your JSONL files with embeddings
                dimensions=EMBEDDING_DIMENSION,
                approximate_neighbors_count=VS_APPROX_NEIGHBORS_COUNT,
                distance_measure_type=VS_DISTANCE_MEASURE_TYPE,
                leaf_nodes_ah_config={
                    "leaf_nodes_to_search_percent": VS_LEAF_NODES_TO_SEARCH_PERCENT,
                },
                description=f"Vector index for RAG using {VS_INDEX_DISPLAY_NAME} embeddings."
            )
            logger.info(f"Vector Search Index {index.resource_name} creation initiated.")
            index.wait() # Wait for index creation to complete
            logger.info(f"Vector Search Index {index.resource_name} is ready.")

        # Export the index resource name for later deployment
        with open("vs_index_resource_name.txt", "w") as f:
            f.write(index.resource_name)
        logger.info(f"Vector Search Index resource name saved to vs_index_resource_name.txt: {index.resource_name}")

    except Exception as e:
        logger.error(f"Error managing Vector Search Index: {e}")
        raise

if __name__ == "__main__":
    required_vars = ["GCP_PROJECT_ID", "GCP_REGION", "VS_INDEX_DISPLAY_NAME",
                     "VS_DATA_GCS_URI", "EMBEDDING_DIMENSION", "VS_DISTANCE_MEASURE_TYPE",
                     "VS_APPROX_NEIGHBORS_COUNT", "VS_LEAF_NODES_TO_SEARCH_PERCENT"]
    if not all(os.environ.get(var) for var in required_vars):
        logger.error("Missing one or more required environment variables. Please set them in your bash script.")
        exit(1)

    manage_vector_search_index()