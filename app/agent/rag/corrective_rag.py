from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple
import requests
import os

class CorrectiveRAG:
    """
    Corrective RAG Pipeline
    Evaluates retrieval quality and corrects
    bad retrievals before generation
    """

    def __init__(self):
        # Lightweight embedder — runs on CPU fine
        self.embedder = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        # Local Qdrant
        self.qdrant = QdrantClient(
            host="localhost", port=6333
        )

        self.collection = "health_knowledge"

        # Relevance threshold
        # Score below this = retrieval is bad
        # Trigger correction step
        self.relevance_threshold = 0.5

        print("✅ CorrectiveRAG initialized")

    # ── Step 1: Retrieve ──────────────────────────
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category_filter: str = None
    ) -> List[Dict]:

        query_vector = self.embedder.encode(
            query, normalize_embeddings=True
        ).tolist()

        # Build filter if category specified
        search_filter = None
        if category_filter:
            search_filter = Filter(
                must=[FieldCondition(
                    key   = "category",
                    match = MatchValue(
                        value=category_filter
                    )
                )]
            )

        results = self.qdrant.search(
            collection_name = self.collection,
            query_vector    = query_vector,
            query_filter    = search_filter,
            limit           = top_k,
            with_payload    = True,
            score_threshold = 0.3  # minimum score
        )

        docs = []
        for r in results:
            docs.append({
                "text":     r.payload.get("text",""),
                "source":   r.payload.get("source",""),
                "category": r.payload.get("category",""),
                "score":    r.score
            })

        return docs

    # ── Step 2: Evaluate Relevance ────────────────
    def evaluate_relevance(
        self,
        query: str,
        docs: List[Dict]
    ) -> Tuple[str, float]:
        """
        Evaluate if retrieved docs are relevant
        Returns: (decision, avg_score)
        decision = 'correct' | 'incorrect' | 'ambiguous'
        """
        if not docs:
            return 'incorrect', 0.0

        scores = [d['score'] for d in docs]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)

        if max_score >= self.relevance_threshold:
            return 'correct', avg_score
        elif avg_score >= 0.35:
            return 'ambiguous', avg_score
        else:
            return 'incorrect', avg_score

    # ── Step 3: Correct (Web Search fallback) ─────
    def web_search_fallback(
        self, query: str
    ) -> List[Dict]:
        """
        Called when retrieval quality is poor.
        Uses DuckDuckGo free search — no API key.
        """
        try:
            from duckduckgo_search import DDGS

            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(
                    f"medical {query}",
                    max_results=3
                ):
                    results.append({
                        "text":     r.get('body',''),
                        "source":   "web_search",
                        "category": "web",
                        "score":    0.5
                    })
            return results

        except Exception as e:
            print(f"Web search failed: {e}")
            return []

    # ── Step 4: Generate via HuggingFace API ──────
    def generate_answer(
        self,
        query: str,
        context_docs: List[Dict]
    ) -> str:
        """
        Uses HuggingFace Inference API
        Free tier — no GPU needed locally
        Calls your fine-tuned BioMistral model
        """
        # Build context from retrieved docs
        context = "\n\n".join([
            f"[Source: {d['source']}]\n{d['text'][:300]}"
            for d in context_docs[:3]
        ])

        # Build prompt
        prompt = f"""### Question:
{query}

### Relevant Medical Context:
{context}

### Answer:
Based on the medical context provided,"""

        # Call HuggingFace Inference API
        # Free tier: 1000 requests/day
        HF_TOKEN  = os.getenv("HF_TOKEN")
        if not HF_TOKEN:
            return "Generation failed: HF_TOKEN not found in environment variables."

        MODEL_URL = (
            "https://api-inference.huggingface.co"
            "/models/asadullahshehbaz/"
            "biomistral-health-fyp"
        )

        print(f"  Requesting HF API: {MODEL_URL}")

        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }
        payload = {
            "inputs":     prompt,
            "parameters": {
                "max_new_tokens":     300,
                "temperature":        0.7,
                "return_full_text":   False,
                "do_sample":          True,
            }
        }

        try:
            response = requests.post(
                MODEL_URL,
                headers = headers,
                json    = payload,
                timeout = 30
            )
            
            # Check for HTTP errors first
            if response.status_code != 200:
                return f"Generation failed: API returned status {response.status_code}. Content: {response.text[:100]}"

            result = response.json()

            if "error" in result:
                return f"Generation failed: {result['error']}"

            if isinstance(result, list):
                return result[0].get(
                    'generated_text', ''
                ).strip()
            else:
                return str(result)

        except Exception as e:
            return f"Generation failed: {e}"

    # ── Main Pipeline: Full C-RAG Flow ────────────
    def run(self, patient_query: str) -> Dict:
        """
        Complete Corrective RAG pipeline
        Returns full diagnostic result
        """
        print(f"\n{'='*50}")
        print(f"Query: {patient_query[:80]}")
        print(f"{'='*50}")

        # Step 1 — Initial retrieval
        print("Step 1: Retrieving documents...")
        docs = self.retrieve(patient_query, top_k=5)
        print(f"  Retrieved: {len(docs)} documents")

        # Step 2 — Evaluate relevance
        print("Step 2: Evaluating relevance...")
        decision, avg_score = self.evaluate_relevance(
            patient_query, docs
        )
        print(f"  Decision: {decision} "
              f"(avg score: {avg_score:.3f})")

        # Step 3 — Correct if needed
        if decision == 'incorrect':
            print("Step 3: CORRECTING — web search...")
            web_docs = self.web_search_fallback(
                patient_query
            )
            docs = web_docs + docs  # prepend web results
            print(f"  Added {len(web_docs)} web docs")

        elif decision == 'ambiguous':
            print("Step 3: AMBIGUOUS — adding web docs...")
            web_docs = self.web_search_fallback(
                patient_query
            )
            docs = docs + web_docs  # append web results
            print(f"  Added {len(web_docs)} web docs")

        else:
            print("Step 3: Retrieval CORRECT — no correction needed")

        # Step 4 — Generate answer
        print("Step 4: Generating answer...")
        answer = self.generate_answer(
            patient_query, docs
        )

        return {
            "query":        patient_query,
            "answer":       answer,
            "sources":      [d['source'] for d in docs[:3]],
            "retrieval":    decision,
            "avg_score":    round(avg_score, 3),
            "docs_used":    len(docs),
            "context_docs": docs[:3]
        }