from model.faiss_index import FAISSIndex
from model.prompt_engine import PromptEngine
from model.openai_model import OpenAIModel
from custom_logger import logger

from langchain.docstore.document import Document
from typing import List, Tuple

from api.model.output import Output as AdviceOutput
from api.model.metadata import Metadata 

from configurations import config
model_config = config.ModelConfig()

class RAGEngine:
    """
    A class to handle the RAG (Retrieval-Augmented Generation) engine.
    
    Attributes
    ----------
    embedding_model : EmbeddingModel
        The model used for generating embeddings.
    faiss_index_loader : FAISSIndexLoader
        The loader for managing the FAISS index.
    """
    
    def __init__(self) -> None:
        """
        Initializes the RAG engine with the embedding model and FAISS index loader.
        """
        self.vectorstore = FAISSIndex().load_index()
        self.prompt_engine = PromptEngine()
        self.openai_model = OpenAIModel()

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        try:
            return self.vectorstore.similarity_search_with_score(query, k=k)
        except Exception as e:
            logger._log(f"Error during retrieval: {e}", format="error")
            return []
    
    def run_rag_pipeline(self, query: str) -> AdviceOutput:
        """
        Runs the RAG pipeline to retrieve relevant documents and generate a response.
        
        Parameters
        ----------
        query : str
            The user's query for which to generate a response.
        
        Returns
        -------
        JSON
            The generated response in JSON format.
        """
        documents = self.retrieve(query, k=5)
        if not documents:
            return AdviceOutput(advice="No relevant Documents found", 
                                retrievedDocuments=[], 
                                metadata=Metadata(
                                    retrievalScores=[],
                                    embeddingsModel=model_config.MODEL_NAME,
                                    promptUsed=self.prompt_engine.prompt.format(query=query, context="")
                                ))        
        chunks, prompt = self.prompt_engine.build_prompt(query, documents, self.openai_model)
        advice: str = self.openai_model.generate_response(prompt, self.prompt_engine.functions)
        meta: Metadata = Metadata(
            retrievalScores=[score for _, score in documents],
            embeddingsModel=model_config.MODEL_NAME,
            promptUsed=prompt
        )
        return AdviceOutput(advice=advice, retrievedDocuments=chunks, metadata=meta)