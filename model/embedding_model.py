from langchain_huggingface import HuggingFaceEmbeddings
from configurations import config

model_config = config.ModelConfig()

class EmbeddingModel:
    """
    A class to handle the embedding model for text embeddings.
    
    Attributes
    ----------
    embedding_model : HuggingFaceEmbeddings
        The embedding model used to generate embeddings from text.
    """
    
    def __init__(self) -> None:
        """
        Initializes the EmbeddingModel with the specified configuration.
        """
        self.embedding_model = HuggingFaceEmbeddings(model_name=model_config.MODEL_NAME)
    
    def get_embedding(self, text: str) -> list:
        """
        Generates an embedding for the given text.
        
        Parameters
        ----------
        text : str
            The input text for which to generate an embedding.
        
        Returns
        -------
        list
            The generated embedding as a list of floats.
        """
        return self.embedding_model.embed_query(text)