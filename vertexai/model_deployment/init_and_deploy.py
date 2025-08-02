from google.cloud import aiplatform
import os

PROJECT_ID = os.environ["PROJECT_ID"]
REGION = os.environ["REGION"]
REPO_NAME = os.environ["REPO_NAME"]
IMAGE_NAME = os.environ["IMAGE_NAME"]
IMAGE_URI = os.environ["IMAGE_URI"]

MODEL_NAME = os.environ["MODEL_NAME"]
MODEL_DESCRIPTION = os.environ["MODEL_DESCRIPTION"]
ARTIFACT_BUCKET = os.environ["ARTIFACT_BUCKET"]
ARTIFACT_URI = os.environ["ARTIFACT_URI"]


# Initialize AI Platform client
aiplatform.init(project=PROJECT_ID, location=REGION)

# Upload your locally saved model artifacts to GCS (if not already there)
# os.system(f"gsutil cp -r ./all-MiniLM-L6-v2-model {ARTIFACT_URI}/")
# Make sure to create the bucket if it doesn't exist: gsutil mb gs://your-gcp-project-id-vertex-ai-bucket

# Create the Model resource in Model Registry
model = aiplatform.Model.upload(
    display_name=MODEL_NAME,
    artifact_uri=ARTIFACT_URI,
    serving_container_image_uri=IMAGE_URI,
    description=MODEL_DESCRIPTION,
    serving_container_predict_route="/predict",
    serving_container_health_route="/health",
    serving_container_ports=[8080],
    serving_container_environment_variables={"AIP_MODEL_DIR": "/gcs/" + ARTIFACT_URI.split('gs://')[1]}, # Explicitly set AIP_MODEL_DIR to match GCS path
    # If your model needs specific arguments to start the server:
    # serving_container_args=[
    #     "/usr/bin/python3",
    #     "-m",
    #     "google.cloud.aiplatform.prediction.model_server"
    # ],
    # The default entrypoint in the Dockerfile usually handles this if using google.cloud.aiplatform.prediction.model_server
)

print(f"Model {model.display_name} uploaded with resource name: {model.resource_name}")

endpoint = model.deploy(
    machine_type="n1-standard-4", # Or a suitable machine type, you can also mention gpu usage
    min_replica_count=1,
    max_replica_count=1 
)

print(f"Model deployed to Endpoint: {endpoint.display_name}")
print(f"Endpoint name: {endpoint.resource_name}")