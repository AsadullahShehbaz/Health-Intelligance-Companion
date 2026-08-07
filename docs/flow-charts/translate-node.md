# Flow Diagram

```text
                AgentState
                    │
                    ▼
         translate_in_node()
                    │
                    ▼
      detect_language(raw_input)
                    │
                    ▼
     Save detected_lang to state
                    │
                    ▼
      Translate to English
                    │
                    ▼
 Save english_query into state
                    │
                    ▼
      Next LangGraph Nodes
      (Router → RAG → LLM)
                    │
                    ▼
       LLM generates answer
                    │
                    ▼
      translate_out_node()
                    │
          detected_lang == "en"?
              │             │
            Yes             No
              │             │
              ▼             ▼
      Use answer      Translate back
              │             │
              └──────┬──────┘
                     ▼
        Save final_response
                     │
                     ▼
             Return Response
```

