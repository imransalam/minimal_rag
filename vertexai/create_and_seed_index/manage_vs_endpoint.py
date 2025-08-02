import os
from google.cloud import aiplatform
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
REGION = os.environ.get("GCP_REGION")
VS_INDEX_DISPLAY_NAME = os.environ.get("VS_INDEX_DISPLAY_NAME") # To form deployed index ID
VS_ENDPOINT_DISPLAY_NAME = os.environ.get("VS_ENDPOINT_DISPLAY_NAME")

# For deployment
MACHINE_TYPE = "n1-standard-4" 
MIN_REPLICA_COUNT = 1
MAX_REPLICA_COUNT = 1 

aiplatform.init(project=PROJECT_ID, location=REGION)

def manage_vector_search_endpoint():
    logger.info("Starting to manage Vertex AI Vector Search Endpoint...")

    # Get the index resource name from the file created in the previous step
    try:
        with open("vs_index_resource_name.txt", "r") as f:
            index_resource_name = f.read().strip()
        index = aiplatform.MatchingEngineIndex(index_name=index_resource_name)
    except FileNotFoundError:
        logger.error("Error: vs_index_resource_name.txt not found. Did the index creation step complete successfully?")
        exit(1)
    except Exception as e:
        logger.error(f"Error loading index: {e}")
        exit(1)

    # Find existing endpoint by display name
    index_endpoint = None
    try:
        existing_endpoints = aiplatform.MatchingEngineIndexEndpoint.list(filter=f'display_name="{VS_ENDPOINT_DISPLAY_NAME}"')
        if existing_endpoints:
            index_endpoint = existing_endpoints[0]
            logger.info(f"Found existing Vector Search Index Endpoint: {index_endpoint.resource_name}. Redeploying index to it.")
            
            # Undeploy any existing index with the same ID before deploying the new one
            # This is important if you are always using the same deployed_index_id
            deployed_index_id_to_check = f"{VS_INDEX_DISPLAY_NAME.replace('-', '_')}_v1"
            for deployed_idx in index_endpoint.deployed_indexes:
                if deployed_idx.id == deployed_index_id_to_check:
                    logger.info(f"Undeploying existing deployed index {deployed_idx.id} from endpoint {index_endpoint.resource_name}...")
                    undeploy_op = index_endpoint.undeploy_index(deployed_idx.id)
                    undeploy_op.wait()
                    logger.info(f"Undeployed {deployed_idx.id}.")
                    break # Assuming only one deployed_index_id of this type per endpoint

            deploy_op = index_endpoint.deploy_index(
                index=index,
                deployed_index_id=deployed_index_id_to_check, # Unique ID for this deployment
                machine_type=MACHINE_TYPE,
                min_replica_count=MIN_REPLICA_COUNT,
                max_replica_count=MAX_REPLICA_COUNT
            )
            logger.info(f"Vector Search Index deployment initiated. Operation: {deploy_op.name}")
            deploy_op.wait()
            logger.info(f"Vector Search Index deployed to Endpoint: {index_endpoint.resource_name}.")
        else:
            logger.info("No existing Vector Search Index Endpoint found. Creating a new one.")
            index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
                display_name=VS_ENDPOINT_DISPLAY_NAME,
                # network=None # Optional: Set to your VPC network for private endpoint
            )
            logger.info(f"Vector Search Index Endpoint {index_endpoint.resource_name} creation initiated.")
            index_endpoint.wait() # Wait for endpoint to be ready

            deploy_op = index_endpoint.deploy_index(
                index=index,
                deployed_index_id=f"{VS_INDEX_DISPLAY_NAME.replace('-', '_')}_v1", # Unique ID for this deployment
                machine_type=MACHINE_TYPE,
                min_replica_count=MIN_REPLICA_COUNT,
                max_replica_count=MAX_REPLICA_COUNT
            )
            logger.info(f"Vector Search Index deployment initiated. Operation: {deploy_op.name}")
            deploy_op.wait() # Wait for deployment to complete
            logger.info(f"Vector Search Index deployed to Endpoint: {index_endpoint.resource_name}.")

        # Export the endpoint ID for later use (e.g., in your FastAPI app)
        with open("vs_endpoint_id.txt", "w") as f:
            f.write(index_endpoint.name.split('/')[-1]) # Extract just the ID
        logger.info(f"Vector Search Endpoint ID saved to vs_endpoint_id.txt: {index_endpoint.name.split('/')[-1]}")
        logger.info(f"Vector Search Endpoint resource name: {index_endpoint.resource_name}")

    except Exception as e:
        logger.error(f"Error managing Vector Search Endpoint: {e}")
        raise

if __name__ == "__main__":
    required_vars = ["GCP_PROJECT_ID", "GCP_REGION", "VS_INDEX_DISPLAY_NAME",
                     "VS_ENDPOINT_DISPLAY_NAME"]
    if not all(os.environ.get(var) for var in required_vars):
        logger.error("Missing one or more required environment variables. Please set them in your bash script.")
        exit(1)

    manage_vector_search_endpoint()