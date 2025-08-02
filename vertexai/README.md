# Vertex AI deployment

## **Vertex AI Custom Model Deployment: all-MiniLM-L6-v2 Sentence-Transformer**

This repository contains all the necessary files to deploy a sentence-transformers/all-MiniLM-L6-v2 model as a custom prediction service on Google Cloud's Vertex AI.

The process involves three main steps:

1. **Save the Model:** Download the pre-trained model to your local environment.
2. **Build and Push a Custom Docker Container:** Create a container with the necessary dependencies and a custom prediction handler.
3. **Deploy to Vertex AI:** Upload the model artifacts and deploy the container to a Vertex AI Endpoint.

## **Files**

- build_and_deploy.sh: A shell script to automate the entire process, from creating a Docker repository to deploying the model.
- init_and_deploy.py: A Python script that uses the google-cloud-aiplatform SDK to upload the model artifacts and deploy the custom container.
- Dockerfile: Defines the custom container environment, including dependencies and the entry point for the prediction server.
- requirements.txt: Lists the Python libraries required for the custom prediction routine and the Vertex AI model server.
- predictor.py: The core prediction handler class that loads the model and serves predictions. This is the custom routine that Vertex AI will use.
- save_locally.py: A simple Python script to download the pre-trained all-MiniLM-L6-v2 model from Hugging Face and save it to a local directory.

## **Prerequisites**

Before you begin, ensure you have the following installed and configured:

- A Google Cloud Project with billing enabled.
- The gcloud CLI tool installed and authenticated (gcloud auth login and gcloud config set project &lt;PROJECT_ID&gt;).
- Docker installed and running on your machine.
- Python 3.12 or later.
- The google-cloud-sdk and gsutil components of the gcloud CLI.

## **How to Run**

Follow these steps in the order provided to deploy your model.

### **1\. Configure the build_and_deploy.sh script**

Open the build_and_deploy.sh file and update the variables to match your Google Cloud Project settings.

- PROJECT_ID: Your GCP project ID.
- REGION: The Google Cloud region where you want to deploy the model (e.g., europe-west3).
- REPO_NAME: The name for your Artifact Registry Docker repository.
- IMAGE_NAME: The name for your custom Docker image.
- MODEL_NAME: A display name for your model in Vertex AI.
- ARTIFACT_BUCKET: The name of the GCS bucket where the model artifacts will be stored. This bucket must be in the same region as your Vertex AI deployment.

### **2\. Update the requirements.txt file**

The Dockerfile depends on this file to install the required Python packages. Ensure the file contains all necessary dependencies for the model serving container. The provided requirements.txt file is already correct:

sentence-transformers  
numpy  
google-cloud-aiplatform  
torch  
fastapi\[standard\]  
google-cloud-aiplatform\[prediction\]>=1.16.0  

### **3\. Execute the build_and_deploy.sh script**

This single script will handle the entire deployment pipeline.

1. Open a terminal in the directory containing all the files.
2. Make the script executable:  
    chmod +x build_and_deploy.sh  

3. Run the script:  
    ./build_and_deploy.sh  

### **What the script does:**

- Enables the Artifact Registry API if it's not already enabled.
- Creates a new Docker repository in Artifact Registry.
- Configures Docker to use gcloud for authentication with the repository.
- Builds a new Docker image based on your Dockerfile and pushes it to Artifact Registry.
- Runs save_locally.py to download the model artifacts to a local directory.
- Uploads the local model directory to the Google Cloud Storage bucket.
- Runs init_and_deploy.py to upload the model to Vertex AI and deploy it to a new Endpoint.

### **4\. Verify Deployment**

After the script completes successfully, you will see a message in the console indicating that the model has been deployed to an Endpoint.

You can then navigate to the Vertex AI Endpoints section in the Google Cloud Console to see your newly deployed model and interact with it.

If you encounter any errors, please review the output of the script for details. The most common issues are incorrect permissions, missing environment variables, or dependency conflicts within the Docker container.


## **Vertex AI Vector Search Setup for RAG**

This project provides a set of scripts to automate the creation and deployment of a Vertex AI Vector Search index and endpoint. This is a crucial step for building a Retrieval Augmented Generation (RAG) system, where you embed your own data and use it to retrieve context for a large language model.

The workflow is managed by a single shell script, which orchestrates the execution of several Python scripts.

## **Workflow Overview**

1. **Generate Embeddings:** A Python script reads text from a CSV file, generates embeddings for each text snippet using a deployed Vertex AI embedding model, and saves the embeddings to a local JSONL file.
2. **Upload to GCS:** The local JSONL file is uploaded to a Google Cloud Storage (GCS) bucket.
3. **Create/Update Index:** A Python script uses the GCS data to create or update a Vertex AI Vector Search index.
4. **Deploy Endpoint:** A final Python script deploys the index to a new or existing Vector Search endpoint, making it queryable.

## **Files**

- build_and_deploy.sh: The main shell script that orchestrates the entire process. It sets up environment variables and calls the other Python scripts in the correct order.
- generate_vs_data.py: A Python script that connects to a deployed embedding model, reads data from a GCS CSV file, and generates embeddings. It outputs a embeddings_data.jsonl file.
- manage_vs_index.py: A Python script to programmatically create a new Vertex AI Vector Search index or find an existing one. It waits for the index creation to complete.
- manage_vs_endpoint.py: A Python script to programmatically create a new Vertex AI Vector Search endpoint or find an existing one, and then deploy the index to it.

## **Prerequisites**

- A Google Cloud Project with billing enabled.
- The gcloud CLI tool installed and authenticated (gcloud auth login and gcloud config set project &lt;PROJECT_ID&gt;).
- The Vertex AI and Storage APIs enabled for your project.
- A deployed Vertex AI embedding model (e.g., sentence-transformers/all-MiniLM-L6-v2) and its Endpoint ID.
- A CSV file containing your text data uploaded to a GCS bucket.

## **How to Run**

### **1\. Configure the build_and_deploy.sh script**

Open the build_and_deploy.sh file and update the following environment variables. This is the most critical step.

- **GCP_PROJECT_ID**: Your Google Cloud project ID.
- **GCP_REGION**: The region for your Vertex AI and GCS resources (e.g., europe-west3).
- **RAW_DATA_GCS_BUCKET**: The GCS bucket containing your raw CSV data.
- **VS_INPUT_GCS_BUCKET**: A GCS bucket for the intermediate JSONL embedding files.
- **EMBEDDING_ENDPOINT_ID**: The numeric ID of your deployed Vertex AI embedding model.
- **VS_INDEX_DISPLAY_NAME**: A human-readable name for your Vector Search index.
- **VS_ENDPOINT_DISPLAY_NAME**: A human-readable name for your Vector Search endpoint.
- **CSV_GCS_PATH**: The full GCS path to your input CSV file (e.g., gs://my-bucket/quotes.csv).
- **CSV_COLUMN_NAME**: The name of the column in your CSV that contains the text to be embedded.
- **EMBEDDING_DIMENSION**: The output dimension of your embedding model (384 for all-MiniLM-L6-v2).
- **VS_DISTANCE_MEASURE_TYPE**: The distance measure for the index (e.g., DOT_PRODUCT_DISTANCE).
- **VS_APPROX_NEIGHBORS_COUNT**: The number of approximate neighbors to retrieve per query.
- **VS_LEAF_NODES_TO_SEARCH_PERCENT**: The percentage of the index to search.

### **2\. Run the deployment script**

Once the configuration is complete, you can run the entire workflow with a single command.

1. Open a terminal in the directory where your files are located.
2. Make the script executable:  
    chmod +x build_and_deploy.sh  

3. Execute the script:  
    ./build_and_deploy.sh  

The script will log its progress as it performs each step, from generating embeddings to deploying the final endpoint.

### **3\. Verify Deployment**

After the script successfully completes, you will see the final output with the resource names for your Vector Search index and endpoint. You can also verify the deployment in the Google Cloud Console under the Vertex AI -> Vector Search section.