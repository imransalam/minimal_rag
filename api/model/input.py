from pydantic import BaseModel, Field

class Input(BaseModel):
    """
    Data model for the input.
    
    Attributes
    ----------
    query : str
        An issue you want to ask famous people.
    """
    query: str = Field(..., description="The issue you want to ask famous people")
