FROM python:3.12-slim-bookworm

# Set the working directory in the container
WORKDIR /app

COPY seed_index /app/seed_index
COPY gcp_utils /app/gcp_utils
COPY data /app/data
COPY configurations /app/configurations
COPY custom_logger /app/custom_logger
COPY model/ /app/model
COPY api /app/api
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE 8080
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]