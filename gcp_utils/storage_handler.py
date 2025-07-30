"""
This module provides utility functions for interacting with Google Cloud Storage.
It includes functionalities to write index to the storage and read it back.

Configuration:
- Relies on Config for project and bucket configurations.

Dependencies:
- google-cloud-storage: Google Cloud Client Library for Python.
"""
from google.cloud import storage
from configurations.config import Config
import os

# Initialize configuration and storage client
config = Config()

def _write_to_cloud_storage(folder_path: str) -> None:
    """
    Upload a the FAISS index to a specified path in Google Cloud Storage.

    Parameters
    ----------
    index : str
        The serialized FAISS index to upload.
    folder_path : str
        The destination folder path within the cloud storage bucket.

    Returns
    -------
    None
    """
    storage_client = storage.Client(config.PROJECT_NAME)
    bucket = storage_client.bucket(config.BUCKET_NAME)
    for file in os.listdir(folder_path):
        local_path = os.path.join(folder_path, file)
        if os.path.isfile(local_path):
            blob = bucket.blob(os.path.join(folder_path, file))
            blob.upload_from_filename(local_path)
            print(f"Uploaded {file} to GCS at {folder_path}.")

def _read_from_cloud_storage(folder_path: str) -> None:
    """
    Download a folder from Google Cloud Storage.

    Parameters
    ----------
    folder : str
        The folder path within the cloud storage bucket to download from.

    Returns
    -------
    None
    """
    storage_client = storage.Client(config.PROJECT_NAME)
    bucket = storage_client.bucket(config.BUCKET_NAME)
    os.makedirs(folder_path, exist_ok=True)
    required_files = ["index.faiss", "index.pkl"]
    for file_name in required_files:
        blob_path = os.path.join(folder_path, file_name)
        local_path = os.path.join(folder_path, file_name)
        blob = bucket.blob(blob_path)
        if blob.exists():
            blob.download_to_filename(local_path)
            print(f"Downloaded {file_name} from GCS to {local_path}.")
        else:
            print(f"File {blob_path} does not exist in GCS.")
    
def _check_index_exists(folder_path: str) -> bool:

    """
    Check if the FAISS index exists in the specified folder path in Google Cloud Storage.

    Parameters
    ----------
    folder_path : str
        The folder path within the cloud storage bucket to check for the index.
    Returns
    -------
    bool
    """
    storage_client = storage.Client(config.PROJECT_NAME)
    bucket = storage_client.bucket(config.BUCKET_NAME)
    try:
        required_files = {f"{folder_path}/index.faiss", f"{folder_path}/index.pkl"}
        blobs = bucket.list_blobs(prefix=folder_path)

        existing_files = {blob.name for blob in blobs}
        return required_files.issubset(existing_files)
    except:
        return False
