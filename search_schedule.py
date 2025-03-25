import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Load the schedule with embeddings
file_path = r"C:\Users\afnan baba\Desktop\MOOSA\mohib umair moosa project\Updated_Schedule_with_Embeddings.xlsx"
df = pd.read_excel(file_path)

# Load the same model used for generating embeddings
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Convert stored string embeddings back to lists
import ast
df['embeddings'] = df['embeddings'].apply(ast.literal_eval)

# Get user query
query = "Data Structures and Algorithms"
query_embedding = model.encode(query, convert_to_tensor=True)

# Compute similarity scores
embeddings = [model.encode(text, convert_to_tensor=True) for text in df['context']]
similarities = [util.pytorch_cos_sim(query_embedding, emb)[0][0].item() for emb in embeddings]

# Add similarity scores to DataFrame
df['similarity'] = similarities

# Sort results by similarity (highest first)
df_sorted = df.sort_values(by='similarity', ascending=False)

# Display top 5 matching results
top_results = df_sorted[['context', 'similarity']].head(5)
print("\nTop Matching Results:\n", top_results)
