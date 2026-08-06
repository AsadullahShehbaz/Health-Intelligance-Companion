from pprint import pprint

from app.core.rag.corrective_rag import corrective_retrieve

result = corrective_retrieve(
    "What are the symptoms of diabetes?"
)

pprint(result)

print("\nDecision:", result["decision"])
print("Average Score:", result["avg_score"])
print("Documents Used:", len(result["docs"]))

print("\nRetrieved Documents:\n")

for i, doc in enumerate(result["docs"], start=1):
    print(f"{i}. Source   : {doc['source']}")
    print(f"   Category : {doc['category']}")
    print(f"   Score    : {doc['score']}")
    print(f"   Text     : {doc['text'][:200]}...\n")