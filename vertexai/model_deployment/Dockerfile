FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your custom prediction routine
COPY predictor.py .

# Create a directory for your model artifacts (Vertex AI expects this)
# The AIP_MODEL_DIR environment variable will point to this location
# when the model artifacts are copied into the container by Vertex AI.
RUN mkdir /app/model

# Set the entrypoint for the prediction server
# This tells Vertex AI how to run your custom prediction routine.
# The `CustomPredictor` class should be exposed.
ENV CLOUD_ML_MODEL_NAME=all-minilm-l6-v2
ENV CLOUD_ML_PREDICTOR_CLASS=predictor.CustomPredictor

ENTRYPOINT ["python", "-m", "google.cloud.aiplatform.prediction.model_server"]

