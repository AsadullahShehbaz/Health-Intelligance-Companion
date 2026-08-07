
```text
                    User Query + Recent Memory
                              │
                              ▼
        ┌────────────────────────────────────────┐
        │ Context Preparation                    │
        │────────────────────────────────────────│
        │ • Retrieve Recent Memory               │
        │ • Format Conversation History          │
        │ • Combine with Current User Query      │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────┐
        │ Prompt Construction                    │
        │────────────────────────────────────────│
        │ REWRITER_PROMPT                        │
        │ • Conversation Context                 │
        │ • Current User Query                   │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
        ┌────────────────────────────────────────┐
        │ Query Rewriter Agent (LLM)             │
        │────────────────────────────────────────│
        │ • Rewrite Medical Query                │
        │ • Remove Ambiguity                     │
        │ • Preserve User Intent                 │
        │ • Generate Search-Friendly Query       │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
              ┌────────────▼────────────┐
              │ Rewritten Query Empty ? │
              └────────────┬────────────┘
                           │
                   No      │      Yes
                    │      │
                    ▼      ▼
      ┌─────────────────┐  ┌─────────────────────┐
      │ Rewritten Query │  │ Original User Query │
      │                 │  │ (Fallback)          │
      └────────┬────────┘  └──────────┬──────────┘
               │                      │
               └──────────┬───────────┘
                          ▼
        ┌────────────────────────────────────────┐
        │ Update Agent State                     │
        │ rewritten_query                        │
        └──────────────────┬─────────────────────┘
                           │
                           ▼
                     Next Pipeline Node
```



