# src/predictor.py
import os
from sentence_transformers import SentenceTransformer
import numpy as np

class CustomPredictor:
    def __init__(self):
        """Initializes the predictor by loading the model."""
        self._model = None
        self._model_dir = os.environ.get("AIP_MODEL_DIR") # This env var is set by Vertex AI

    def load(self):
        """Loads the model from the specified directory."""
        if not self._model_dir:
            raise ValueError("AIP_MODEL_DIR environment variable is not set.")
        self._model = SentenceTransformer(self._model_dir)
        print(f"Model loaded from {self._model_dir}")

    def predict(self, instances):
        """
        Performs prediction.
        Args:
            instances: A list of strings (sentences) to embed.
        Returns:
            A list of lists, where each inner list is the embedding for a sentence.
        """
        if self._model is None:
            self.load() # Load model if not already loaded (e.g., for local testing)

        # Assuming instances is a list of strings
        if not isinstance(instances, list) or not all(isinstance(i, str) for i in instances):
            raise ValueError("Input 'instances' must be a list of strings.")

        embeddings = self._model.encode(instances, convert_to_numpy=True)
        # Convert numpy array to list for JSON serialization
        return embeddings.tolist()

if __name__ == '__main__':
    # This block is for local testing or when Vertex AI invokes the script directly
    # In a Vertex AI environment, AIP_MODEL_DIR will be set.
    # For local testing, you might set it manually for the script to find the model.
    # export AIP_MODEL_DIR="./all-MiniLM-L6-v2-model" (before running this script)

    predictor = CustomPredictor()
    predictor.load()

    test_sentences = [
        "This is a test sentence.",
        "Another sentence for embedding."
    ]
    predictions = predictor.predict(test_sentences)
    print("Predictions (first 5 values of first embedding):", predictions[0][:5])
    print("Shape:", np.array(predictions).shape)