## Flow Diagram

```text
          AgentState
              │
              ▼
      has_image == True?
         │            │
      No │            │ Yes
        │            ▼
        │   extract_text_from_base64()
        │            │
        │            ▼
        │    OCR Extracted Text
        │            │
        │            ▼
        │  Append text to raw_input
        │            │
        └────────────┴──────────────►
                      │
                      ▼
            Return Updated State
```

