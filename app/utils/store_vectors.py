import os
from database.chroma import collection

# Read text file
file_path ="/Project-Folder/Chroma_db/python.txt"  
if not os.path.exists(file_path):
    raise FileExistsError(f" File {file_path} not found.")

with open(file_path, "r", encoding="utf-8") as file:
    text_content = file.read()

documents = [doc.strip() for doc in text_content.split("\n") if doc.strip()]

# Generate IDs and metadata for each document
ids = [f"doc_{i}" for i in range(len(documents))]
metadatas = [{"source": file_path, "index": i} for i in range(len(documents))]


try:
    collection.add(documents=documents, ids=ids, metadatas=metadatas)

    print(f"Successfully stored {len(documents)} documents in collection")

except Exception as e:
    print(f"Error adding documents to collection: {str(e)}")
    exit(1)
