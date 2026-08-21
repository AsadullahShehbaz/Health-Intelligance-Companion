# Feature Spec: PDF/TXT File Upload → Text Extraction → Agent Context + Memory Extraction

## 1. Goal

Let a user upload a `.pdf` or `.txt` file in the chat. Backend extracts text, passes it to the LangGraph agent as context for that turn, and the existing "remember" node also runs over the extracted text so it can pull durable facts into the Postgres-backed memory store — same as it does today for typed messages.

**Non-goals (call these out explicitly to avoid scope creep):**
- No OCR for scanned/image-only PDFs in v1 (flag as future work)
- No support for docx/csv/images in this pass
- No multi-file batch upload in v1 (one file per message)

---

## 2. High-Level Architecture Change

```
Current:
User (text) → FastAPI /chat → LangGraph(entry) → [remember_node] → [agent_node] → response

New:
User (text + optional file) → FastAPI /chat (multipart)
        → file_service.extract_text(file)   [new]
        → merged_input = user_text + extracted_text
        → LangGraph(entry) → [remember_node] (now doc-aware) → [agent_node] → response
```

Key decision: **extraction happens in the API layer, before the graph is invoked** — not as a LangGraph node itself. This keeps the graph's input contract simple (it always receives text) and keeps PDF-parsing dependencies out of the graph runtime. The "remember node" doesn't need to know a file was involved, only that it received a longer text blob with a `source_type` tag.

---

## 3. New/Changed Components

### 3.1 API layer (FastAPI)
- Change `/chat` endpoint from JSON-only to accept `multipart/form-data`:
  - `message: str` (existing, now optional if file present)
  - `file: UploadFile` (new, optional — `.pdf` or `.txt`)
  - `session_id: str` (existing)
- Add validation middleware:
  - MIME/extension check (`application/pdf`, `text/plain`)
  - Max file size (recommend 10MB cap for v1)
  - Reject empty files

### 3.2 New service: `file_extraction_service.py`
```python
def extract_text(file: UploadFile) -> ExtractedDocument:
    # dispatch by extension/mime
    # .txt  -> decode utf-8 (fallback latin-1), strip null bytes
    # .pdf  -> PyMuPDF (fitz) or pdfplumber for text extraction
    # returns ExtractedDocument(text, page_count, char_count, filename, source_type)
```
- Use **PyMuPDF (`fitz`)** over `pypdf` — faster, better layout handling, already common in LangChain ecosystems.
- Add a hard cap on extracted characters (e.g. 50k chars) with truncation + a flag `was_truncated: bool` so the agent/UI can tell the user.
- If PDF has zero extractable text (scanned image) → return explicit `EMPTY_TEXT` error, not silent empty string. Surface to user: "This looks like a scanned PDF — text couldn't be extracted."

### 3.3 Data model addition
New Postgres table (or reuse existing LangGraph checkpoint metadata if you already store per-message metadata):

```sql
CREATE TABLE uploaded_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    source_type TEXT NOT NULL,      -- 'pdf' | 'txt'
    char_count INT,
    was_truncated BOOLEAN DEFAULT FALSE,
    extracted_text TEXT,             -- store raw extracted text for audit/reprocessing
    created_at TIMESTAMPTZ DEFAULT now()
);
```
This gives you an audit trail and lets you re-run the remember node later without re-uploading.

### 3.4 LangGraph changes

**Input schema change** — extend your graph state (`AgentState` / `TypedDict`) with:
```python
class AgentState(TypedDict):
    messages: list
    document_context: Optional[str]   # new
    document_meta: Optional[dict]     # new: {filename, source_type, was_truncated}
```

**`remember_node` update** — this is the important part per your requirement:
- Currently it likely extracts facts only from `messages[-1]` (the user's latest text turn).
- Update its prompt/extraction call to also include `document_context` when present, with a clear delimiter so the LLM knows what's user-typed vs. file-derived:

```python
extraction_prompt = f"""
User message: {state['messages'][-1]}

{"Uploaded document (" + state['document_meta']['filename'] + "):" if state.get('document_context') else ""}
{state.get('document_context', '')}

Extract durable facts about the user worth remembering long-term.
"""
```
- Tag memories written to the Postgres store with `source: "document"` vs `source: "chat"` (add a column to your existing memory table if not present) — useful for later debugging/trust ("why does the agent think X?").

**`agent_node`** — no structural change needed, just receives the merged context in its input messages as it already does for long text.

---

## 4. Request/Response Contract

**Request** (`POST /chat`, multipart):
| field | type | required |
|---|---|---|
| message | string | no (required if no file) |
| file | file (.pdf/.txt) | no |
| session_id | string | yes |

**Response** (extend existing schema):
```json
{
  "response": "...",
  "document_processed": {
    "filename": "resume.pdf",
    "char_count": 4210,
    "was_truncated": false
  },
  "memories_saved": 2
}
```
`document_processed` is `null` when no file was sent — keeps backward compatibility for existing text-only clients.

---

## 5. Error Handling

| Case | Behavior |
|---|---|
| Unsupported file type | 400, `"Only .pdf and .txt are supported"` |
| File > size limit | 413, `"File exceeds 10MB limit"` |
| Scanned/no-text PDF | 200 with `document_processed.char_count: 0` + message telling user extraction failed, agent still responds to any typed text |
| Corrupt PDF | 422, caught around the `fitz.open()` call |
| Extraction timeout (very large PDF) | Set a processing timeout (e.g. 15s) → 504 |

---

## 6. Security Considerations
- Never execute embedded PDF JavaScript — PyMuPDF doesn't run it by default, but confirm no `--enable-js` flags anywhere.
- Sanitize filename before storing/logging (path traversal).
- Treat extracted text as **untrusted input** the same way you'd treat user chat — no prompt injection immunity, but nothing new here since it flows into the same LLM call path already sanitized by your existing system prompt structure.

---

## 7. Task Breakdown (for sprint planning)

| # | Task | Est. |
|---|---|---|
| 1 | Add multipart handling + validation to `/chat` endpoint | 0.5 day |
| 2 | Build `file_extraction_service.py` (txt + pdf via PyMuPDF) | 1 day |
| 3 | Add `uploaded_documents` table + migration | 0.5 day |
| 4 | Extend `AgentState` schema + wire into graph invocation | 0.5 day |
| 5 | Update `remember_node` prompt + add `source` tagging to memory writes | 1 day |
| 6 | Error handling + truncation logic | 0.5 day |
| 7 | Tests: unit (extraction), integration (full graph run with PDF), edge cases (scanned PDF, huge file, corrupt file) | 1 day |
| 8 | Frontend: file input, upload progress, "extraction failed" state | (frontend team, parallel) |

**Total backend estimate: ~5 days**

---

## 8. Test Cases to Cover
- Plain text PDF → correct extraction + memory saved
- Multi-page PDF (50+ pages) → truncation kicks in correctly
- Scanned/image PDF → graceful empty-text handling, no crash
- `.txt` with non-UTF8 encoding → fallback decode works
- File + message both present → both merged into context
- File only, no message → graph still runs correctly
- Oversized file → rejected before extraction attempted (don't waste compute)

If you want, I can go one level deeper on any piece — e.g. the actual `remember_node` prompt rewrite, the PyMuPDF extraction code, or the Postgres migration script.