from sentence_transformers import SentenceTransformer
import os


model_name = 'all-MiniLM-L6-v2'
model_path = os.path.join('src', 'models', model_name)


if not os.path.exists(model_path):
    print(f"Downloading model '{model_name}' to '{model_path}'...")

    model = SentenceTransformer(model_name)

    model.save(model_path)
    print("Model download complete.")
else:
    print(f"Model already exists at '{model_path}'.")