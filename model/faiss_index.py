from langchain.vectorstores import FAISS
from model.embedding_model import EmbeddingModel
from configurations import config

model_config = config.ModelConfig()

class FAISSIndex:
    def __init__(self) -> None:
        """
        Initializes the FAISS index loader with the model configuration.
        """
        self.embedding_model = EmbeddingModel()
    
    def create_index(self, documents) -> str:
        """
        Creates a FAISS index from the provided documents.
        
        Parameters
        ----------
        documents : list of Document
            The documents to be indexed.
        """
        self.vectorstore = FAISS.from_documents(documents, self.embedding_model.embedding_model)
        self.vectorstore.save_local(model_config.INDEX_PATH)
        return model_config.INDEX_PATH
    
    def load_index(self) -> FAISS:
        """
        Loads the FAISS index from the local path.
        
        Returns
        -------
        FAISS
            The loaded FAISS index.
        """
        return FAISS.load_local(model_config.INDEX_PATH, 
                                self.embedding_model.embedding_model, 
                                allow_dangerous_deserialization=True)