import pandas as pd
from sentence_transformers import SentenceTransformer

# Define the file path to the cleaned schedule
file_path = "Updated_Schedule.xlsx"

# Load the dataset into a DataFrame
df = pd.read_excel(file_path)


# Load the pre-trained transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')


# Check if the 'context' column is in the dataset
if 'context' not in df.columns:
    raise ValueError("Error: 'context' column not found in dataset!")


# Generate embeddings for each row
df['embeddings'] = df['context'].apply(lambda x: model.encode(x).tolist())


print("Generated Embeddings:")
print(df[['context', 'embeddings']].head())

# Save the DataFrame with embeddings
#df.to_excel("Schedule_with_Embeddings.xlsx", index=False)
#print("Embeddings saved successfully in Schedule_with_Embeddings.xlsx")

# Define the save path
save_path = r"C:\Users\afnan baba\Desktop\MOOSA\mohib umair moosa project\Updated_Schedule_with_Embeddings.xlsx"

# Save the DataFrame with embeddings
df.to_excel(save_path, index=False)

print(f"File saved successfully at: {save_path}")

