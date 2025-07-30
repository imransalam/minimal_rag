from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig

from configurations import config
model_config = config.ModelConfig()

class OpenAIModel:
    """
    A class to handle the OpenAI model for generating responses.
    
    Attributes
    ----------
    llm : ChatOpenAI
        The OpenAI chat model used for generating responses.
    """
    
    def __init__(self) -> None:
        """
        Initializes the OpenAI model with the specified configuration.
        """
        self.llm = ChatOpenAI(model=model_config.OPENAI_MODEL_NAME)
    
    def generate_response(self, query: str, functions: list) -> str:
        """
        Generates a response based on the input query.
        
        Parameters
        ----------
        query : str
            The input query for which to generate a response.
        
        Returns
        -------
        str
            The generated response.
        """
        messages = [
            SystemMessage(content="You are a wise advisor. Based on the following advice fragments, answer the user's question thoughtfully."),
            HumanMessage(content=query)
        ]
        config_dict: RunnableConfig = { 
            "tools": functions if functions else [],
            "tool_choice": "auto" if functions else "none"
        }
        try:
            output = self.llm.invoke(
                input=messages,
                config=config_dict
            )
            return str(output.content)
        except Exception as e:
            raise RuntimeError(f"Error generating response: {e}")