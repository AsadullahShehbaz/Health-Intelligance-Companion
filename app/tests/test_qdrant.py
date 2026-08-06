from app.core.rag.qdrant_store import retrieve

docs = retrieve("What are the symptoms of diabetes?")

print("=" * 50)

for doc in docs:
    print(doc["score"])
    print(doc["source"])
    print(doc["text"][:200])
    print("-" * 50)