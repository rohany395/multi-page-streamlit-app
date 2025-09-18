import chromadb
from chromadb.config import Settings
from pathlib import Path

# Initialize ChromaDB client and collection
db_dir = "chroma_db"
chroma_client = chromadb.Client(Settings(persist_directory=db_dir))
collection = chroma_client.get_or_create_collection(name="txt_files")

data_dir = Path("dataFiles")
txt_files = list(data_dir.glob("*.txt"))

for txt_file in txt_files:
    with open(txt_file, "r", encoding="utf-8") as f:
        text = f.read()
        if text.strip():
            collection.add(
                documents=[text],
                metadatas=[{"source": str(txt_file)}],
                ids=[txt_file.stem]
            )

print(f"Chroma DB created with {len(txt_files)} txt files.")
