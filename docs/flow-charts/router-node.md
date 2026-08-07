# Router Architecture View


```text
                 User Query
                      │
                      ▼
      ┌──────────────────────────────────┐
      │ Prompt Construction              │
      │ (Router Prompt Template)         │
      └───────────────┬──────────────────┘
                      │
                      ▼
      ┌──────────────────────────────────┐
      │ Router Agent (LLM)               │
      │──────────────────────────────────│
      │ • Grammar Constrained Decoding   │
      │ • Structured JSON Output         │
      └───────────────┬──────────────────┘
                      │
                      ▼
      ┌──────────────────────────────────┐
      │ Pydantic Validation              │
      └───────────────┬──────────────────┘
                      │
             ┌────────▼────────┐
             │ Valid Output ?  │
             └──────┬─────┬────┘
                    │Yes  │No
                    │     │
                    ▼     ▼
         Decision Object  Safe Fallback
                    │
                    ▼
      ┌──────────────────────────────────┐
      │ Update Agent State               │
      │ needs_rag                        │
      │ save_memory                      │
      └───────────────┬──────────────────┘
                      │
                      ▼
               Next Agent Node
```


