from configurations import config
from model.openai_model import OpenAIModel

from typing import List, Tuple, Any
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

model_config = config.ModelConfig()

class PromptEngine:
    """
    A class to handle prompt generation and management.
    """
    def __init__(self):
        
        self.prompt = model_config.PROMPT_TEMPLATE
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=model_config.CHUNK_SIZE,
            chunk_overlap=model_config.CHUNK_OVERLAP
        )
        self.functions = [
            {
                "name": "life-advice",
                "description": "Give a life advice based on the user's query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "advice": {
                            "type": "string",
                            "description": "The advice based on the input query"
                        }
                    },
                    "required": ["advice"]
                }
            }
        ]
    def truncate_documents(self, 
                           documents: List[Tuple[Document, float]], 
                           model: Any) -> Tuple[List[str], str]:
        """
        Truncates the documents to fit within the model's context window.
        
        Parameters
        ----------
        documents : List[Tuple[Document, float]]
            The list of documents to truncate.
        
        Returns
        -------
        str
            The concatenated content of the truncated documents.
        """
        all_chunks = []
        for doc, _ in documents:
            all_chunks.extend(self.splitter.split_text(doc.page_content))
        final_context = ""
        for chunk in all_chunks:
            tokens = model.llm.get_num_tokens(final_context + chunk)
            if tokens > model_config.MAX_TOKENS:
                break
            final_context += "\n\n" + chunk

        return all_chunks, final_context.strip()
    
    def build_prompt(self, query: str, 
                     documents: List[Tuple[Document, float]], 
                     model: Any) -> Tuple[List[str], str]:
        """
        Edit the main prompt.
        """
        all_chunks, context = self.truncate_documents(documents, model)
        return all_chunks, self.prompt.format(query=query, context=context)