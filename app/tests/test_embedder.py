from app.core.rag.embedder import embedder

vector = embedder.embed_query(
    "What is diabetes?"
)

print(len(vector))
print(vector[:10])