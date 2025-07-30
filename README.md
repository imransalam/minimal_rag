# **Minimal Retrieval-Augmented Generation (RAG) Pipeline**

## **Overview**

This project implements a minimal RAG pipeline, designed to answer user questions by retrieving relevant information from a knowledge base (FAISS) and leveraging a OpenAI to generate grounded responses.

The pipeline exposes a FastAPI endpoint for querying and returns structured JSON responses.

## **Features**

- **API Endpoint:** A POST /query endpoint to receive user questions.

- **RAG:** Integrates a vector store (FAISS) to
  retrieve relevant document chunks based on user queries.

- **LLM Integration:** Passes retrieved context to an LLM (OpenAI\'s gpt-4o-mini) to generate grounded and thoughtful advice.

- **Structured Output:** Returns responses in a Pydantic-defined JSON format, including the advice, retrieved document summaries, and metadata (retrieval scores, embedding model, prompt used).

- **API Key Authentication:** Secures the API endpoint with a simple API key mechanism.

- **Containerization:** Provides a Dockerfile for easy setup and
  deployment.

- **Structured Logging:** Implements logging for observability of pipeline steps and errors.

- **Fault-Tolerance:** Basic error handling for API and internal pipeline failures.

## **Architecture**

The application follows a layered architecture, built with FastAPI, LangChain, and FAISS.

- **API Layer (api/router/query.py, api/auth.py, api/model/input.py, api/model/output.py):** Handles incoming HTTP requests, performs API key authentication, validates input, and formats responses. It acts as the interface to the RAG pipeline.

- **Service Layer (api/services/query_service.py):** Contains the core business logic for processing a query. It orchestrates calls to the RAG Engine.

- **RAG Engine (model/rag_engine.py):** The heart of the RAG pipeline. It retrieves relevant documents, constructs the prompt, and calls the LLM for generation.

- **Model Components (model/openai_model.py, model/embedding_model.py, model/prompt_engine.py, model/faiss_index.py):**

  - OpenAIModel: Manages interactions with the OpenAI LLM.

  - EmbeddingModel: Handles text vectorization using HuggingFace embeddings.

  - PromptEngine: Responsible for building the LLM prompt and performing document chunking.

  - FAISSIndex: Manages the FAISS vector store for efficient similarity search.

- **Data Ingestion (seed_index/populate_faiss_index.py):** A script to load source documents, process them, create the FAISS index, and optionally persist it to Google Cloud Storage.

- **Storage Utilities (gcp_utils/storage_handler.py):** Provides functions for interacting with Google Cloud Storage for index persistence.

- **Configuration (configurations/config.py):** Centralized
  configuration for API settings, model names, and file paths.

- **Logging (custom_logger.py):** A custom logger for structured logging throughout the application.

## **RAG Details**

### **Retrieval Strategy**

The pipeline uses a vector-based retrieval strategy.

1.  **Embeddings:** User queries are converted into dense vector embeddings using a pre-trained embedding model.

2.  **Vector Store:** These query embeddings are then used to perform a similarity search against a FAISS index, which stores embeddings of pre-processed document chunks.

3.  **Top-K Retrieval:** The retrieve method in RAGEngine fetches the top k (defaulting to 5) most similar document chunks.

### **Embeddings Usage**

- **Model:** The EmbeddingModel utilizes HuggingFaceEmbeddings (e.g., sentence-transformers/all-MiniLM-L6-v2) to generate vector representations of text. 

### **Chunking Strategy**

- **Tool:** RecursiveCharacterTextSplitter from LangChain is employed in PromptEngine to break down large documents into smaller, manageable chunks.

- **Parameters:**

  - chunk_size: Configurable (e.g., model_config.CHUNK_SIZE). This determines the maximum size of each chunk.

  - chunk_overlap: Configurable (e.g., model_config CHUNK_OVERLAP). This specifies the number of characters that overlap between consecutive chunks, helping to preserve context across chunk boundaries.

- **Rationale:** RecursiveCharacterTextSplitter is chosen as it
  intelligently attempts to split text at natural breakpoints (like paragraphs, sentences) before resorting to character-level splitting, thereby maintaining better semantic coherence within chunks. This is crucial for ensuring that retrieved chunks provide meaningful context
  to the LLM.

### **Prompt Engineering**

The PromptEngine constructs the LLM prompt using a template:

self.PROMPT_TEMPLATE: str = \"\"\"
Context:\
{}\
\
Question:\
{}\
\"\"\"

- **Role-Playing:** The LLM is instructed to act as a \"wise advisor.\"

- **Context Injection:** The Context placeholder is dynamically filled with the content of the top k retrieved document chunks. This grounding mechanism ensures the LLM\'s response is based on the provided knowledge base, reducing hallucinations.

- **Question:** The user\'s original query is clearly presented to the LLM.

- **Tool Calling:** The OpenAIModel is configured to use tool calling (specifically, a life-advice function schema is provided in PromptEngine) allowing the LLM to structure its output if it deems appropriate.

### **LLM Integration**

- **Model:** OpenAIModel uses ChatOpenAI (e.g., gpt-40-mini).

## **Documents and Data**

The knowledge base for this RAG pipeline is a small set of quotes by famous people

- **Source:** The data is loaded from a CSV file specified by
  model_config.CSV_PATH. The relevant text column is defined by
  model_config.COLUMN_NAME.

- **Processing:** During the ingestion phase (\_populate_faiss_index), the text from the CSV is converted into LangChain Document objects.

- **Ingestion Flow:** These Document objects are then , embedded using EmbeddingModel, and stored in a FAISS index. The index is saved locally and can optionally be uploaded to Google Cloud Storage for persistence.

## **Observability & Logging**

Structured logging is implemented using custom_logger.py to provide clear insights into the pipeline\'s execution.

## **Error Handling & Fault-Tolerance**

The pipeline incorporates basic error handling to ensure robustness.

- **API Error Responses:** FastAPI\'s HTTPException is used in
  api/router/query.py to return meaningful 500 Internal Server Error responses for unexpected issues, preventing the server from crashing.

- **Retrieval Failure:** In RAGEngine.run_rag_pipeline, if no relevant documents are retrieved, a default \"No relevant Documents found\" message is returned in the structured Output format, preventing the LLM from hallucinating or failing due to lack of context.

- **LLM API Errors:** The OpenAIModel.generate_response method includes a try-except block to catch exceptions during LLM API calls, raising a RuntimeError to propagate the issue.

- **Logging:** All caught exceptions are logged with full tracebacks for easier debugging.

## **Containerization (Docker)**

The application is containerized using Docker, providing a consistent and isolated environment for development and deployment.

### **Setup Instructions**

1.  **Prerequisites:**

    - Python 3.9+

    - Docker Desktop (or Docker Engine on Linux)

2.  **Clone the Repository:**\
    ```
    git clone https://github.com/imransalam/minimal_rag\
    cd minimal_rag
    ```

3.  **Build the Docker Image:**\
    `docker build -t minimal-rag-app .`

4.  **Run the Docker Container:**
    ```
    docker run -p 8080:8080 \
    -e env="local"
    -e OPENAI_API_KEY="sk-xxxx" \
    -e API_AUTH_KEY="xxxxx" \
    minimal-rag-local
    ```


## **Usage**

Once the application is running (either via Docker or locally), you can query the /query endpoint.

### **Querying the API**
Open `0.0.0.0:8080/docs` to get swagger implementation
OR
Send a POST request to `http://0.0.0.0:8080/query` with your question in the request body and your API key in the X-API-Key header.

**Example using curl:**

curl -X POST \"http://0.0.0.0:8080/query\" \\\
-H \"Content-Type: application/json\" \\\
-H \"X-API-Key: your_super_secret_api_key_123\" \\\
-d \'{\
\"query\": \"How can I lead a more fulfilling life?\"\
}\'

**Expected JSON Response Format:**

{\
\"advice\": \"The generated advice based on the query and retrieved
documents.\",\
\"retrievedDocuments\": \[\
\"Summary of relevant document chunk 1\...\",\
\"Summary of relevant document chunk 2\...\"\
\],\
\"metadata\": {\
\"retrievalScores\": \[\
0.95,\
0.88,\
0.72\
\],\
\"embeddingsModel\": \"sentence-transformers/all-MiniLM-L6-v2\",\
\"promptUsed\": \"The full prompt sent to the LLM, including context.\"\
}\
}