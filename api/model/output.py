from api.model.metadata import Metadata
from pydantic import BaseModel, Field
from typing import List

class Output(BaseModel):
    """
    Output data model for an advice.
    
    Attributes
    ----------
    advice: str
        Advise based on the input query
    note: str
        Some precautionary note or additional information related to the advice.
    """
    advice: str = Field(..., description="The advice based on the input query")
    retrievedDocuments: List[str] = Field(..., description="A list of retrieved documents related to the advice that came from top search")
    metadata: Metadata = Field(..., description="Metadata containing retrieval scores, embeddings model, and prompt used")
 