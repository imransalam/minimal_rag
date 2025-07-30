from pydantic import BaseModel, Field
from typing import List

class Metadata(BaseModel):
    """
    Metadata model for storing additional information about the advice.
    
    Attributes
    ----------
    retrievalScores : List[float]
        The scores of the retrieved documents by similarity.
    embeddingsModel : str
        The model used for generating embeddings and similarity.
    promptUsed : str
        The prompt used to generate the final response.
    """
    retrievalScores: List[float] = Field(..., description="The scores of the retrieved documents by similarity")
    embeddingsModel: str = Field(..., description="The model used for generating embeddings and similarity")
    promptUsed: str = Field(..., description="The prompt used to generate the final response")