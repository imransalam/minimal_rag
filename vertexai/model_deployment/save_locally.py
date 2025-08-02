from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Define a directory to save your model artifacts
model_dir = "./all-MiniLM-L6-v2-model"

# Save the model and its tokenizer
model.save_pretrained(model_dir)

print(f"Model saved to {model_dir}")