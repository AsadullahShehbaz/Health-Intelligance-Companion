# **Architecture diagram**.

```
┌──────────────┐
│    USER      │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│      Input Processing         │
│ OCR │ Language │ Translation  │
└──────────────┬───────────────┘
               │
               ▼
        ┌───────────────┐
        │ Router Agent  │
        └──────┬────────┘
               │
      ┌────────┴───────────┐
      ▼                    ▼
Memory Service       Query Rewriter
                           │
                           ▼
                 ┌───────────────────┐
                 │ Corrective RAG    │
                 ├───────────────────┤
                 │ Embedding Model   │
                 │ Qdrant Database   │
                 │ Relevance Check   │
                 │ Web Search        │
                 └─────────┬─────────┘
                           │
                           ▼
                  Medical Reasoner
                           │
                           ▼
                   Memory Storage
                           │
                           ▼
                    Translation Back
                           │
                           ▼
                     Final Response
```


