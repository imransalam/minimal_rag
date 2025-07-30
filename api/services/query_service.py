

from model.rag_engine import RAGEngine
from api.model.output import Output 
from custom_logger import logger 
from api.model.output import Output

class QueryService:
    def __init__(self):
        self.rag_engine = RAGEngine()
        logger._log("QueryService initialized with RAGEngine", format="info")

    def get_life_advice(self, input_query: str) -> Output:
        """
        Executes the RAG pipeline to get life advice.
        This method contains the core business logic.
        """
        logger._log(f"Executing RAG pipeline for query: '{input_query}'", format="info")
        
        # Call the RAG engine
        output_data: Output = self.rag_engine.run_rag_pipeline(input_query)
        
        # Validate and return the Output Pydantic model
        # This ensures the service always returns a well-defined structure
        return output_data