
class Config:
    """
    Base configuration class for sharing common functionality.
    
    This class serves as a parent to specific configurations and 
    can be extended to include shared methods or properties in the future.

    Attributes
    ----------
    COLUMN_NAME : str
        The name of the column in the CSV file that contains the text data.
    INDEX_PATH : str
        The path where the FAISS index will be stored.
    CSV_PATH : str
        The path to the CSV file containing the dataset.
    PROJECT_NAME : str
        The name of the Google Cloud project.
    BUCKET_NAME : str
        The name of the Google Cloud Storage bucket where the index will be stored.
    """
    def __init__(self) -> None:
        self.COLUMN_NAME: str = "quote"
        self.INDEX_PATH: str = "faiss_index"
        self.CSV_PATH: str = "data/quotes.csv"
        self.PROJECT_NAME: str = "my-web-page-230207"
        self.BUCKET_NAME: str = "minimal-rag-bucket"

class ApiConfig(Config):
    """
    Configuration settings for the API server.
    
    Attributes
    ----------
    PORT : int
        The port number on which the server will listen.
    HOST : str
        The host address of the server, typically set to "0.0.0.0" for accessibility.
    """
    def __init__(self) -> None:
        super().__init__()
        self.PORT: int = 8080
        self.HOST: str = "0.0.0.0"

class ModelConfig(Config):
    """
    Configuration settings for the machine learning model and related resources.
    
    Attributes
    ----------
    MODEL_NAME : str
        The name of the model to be used for embeddings, defaulting to a lightweight model.
    TOP_RESULTS : int
        The number of top results to return from the model.
    OPENAI_MODEL_NAME : str
        The name of the OpenAI model to be used for generating responses.
    CHUNK_SIZE : int
        The size of text chunks to be processed by the model.
    CHUNK_OVERLAP : int
        The number of overlapping characters between chunks to maintain context.
    PROMPT_TEMPLATE : str
        The template for prompts used in the model.
    Methods
    -------
    __init__()
        Initializes the configuration and ensures required directories exist.
    """
    def __init__(self) -> None:
        super().__init__()
        self.MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
        self.TOP_RESULTS: int = 5
        self.OPENAI_MODEL_NAME = "gpt-4o-mini"
        self.MAX_TOKENS: int = 2000
        self.CHUNK_SIZE: int = 400
        self.CHUNK_OVERLAP: int = 100
        self.PROMPT_TEMPLATE: str = """
        Context:
        {context}

        Question:
        {query}
        """

