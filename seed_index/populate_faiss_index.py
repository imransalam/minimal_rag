
import os
from configurations import config
from gcp_utils import storage_handler
from custom_logger import logger

model_config = config.ModelConfig()

async def _populate_faiss_index(env: str) -> None:
    """
    Populates the FAISS index with data from a CSV file and saves it to cloud storage.
    
    This function reads a dataset from a CSV file, converts the text data into LangChain Document objects,
    generates embeddings using a specified model, and creates a FAISS index. If the index already exists in
    cloud storage, it skips the creation process.
    """
    logger._log("Starting to populate FAISS index...")
    
    # Check if the FAISS index already exists in cloud storage
    if os.path.exists(os.path.join(model_config.INDEX_PATH, "index.faiss")) and os.path.exists(os.path.join(model_config.INDEX_PATH, "index.pkl")):
        logger._log("FAISS index already exists locally.")
        if env == "local":
            return
        if not storage_handler._check_index_exists(model_config.INDEX_PATH):
            storage_handler._write_to_cloud_storage(model_config.INDEX_PATH)
            logger._log(f"FAISS index saved to cloud storage at {model_config.INDEX_PATH}.")
    elif env != "local" and storage_handler._check_index_exists(model_config.INDEX_PATH):
        logger._log("FAISS index already exists in cloud storage.")
        storage_handler._read_from_cloud_storage(model_config.INDEX_PATH)
    else:
        # 1. Load the quotes dataset
        import pandas as pd
        from langchain.docstore.document import Document
        from model.faiss_index import FAISSIndex
        
        df = pd.read_csv(model_config.CSV_PATH)
        texts = df[model_config.COLUMN_NAME].dropna().tolist()

        # 2. Convert to LangChain Document objects
        documents = [Document(page_content=text) for text in texts]

        # 3. Create the FAISS index
        logger._log("Creating FAISS index...")
        vectorstore: FAISSIndex = FAISSIndex()
        saved_folder: str = vectorstore.create_index(documents)
        if env == "local":
            return
        storage_handler._write_to_cloud_storage(saved_folder)
        logger._log(f"FAISS index created and saved to {saved_folder} in cloud storage.")