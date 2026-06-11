# EvolvIQ — AI-Native Intelligence Workspace

EvolvIQ is an MVP single-user intelligence workspace that demonstrates:

- Autonomous Research Mode
- Knowledge-Augmented Chat
- Structured knowledge extraction
- Evidence traceability
- Memory across sessions
- Knowledge graph updates
- Basic reinforcement and contradiction detection
- Upload processing for PDF, DOCX, XLSX, TXT, and MD

## 1. Setup

```bash
cd evolviq_app
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## 2. Run Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Open:

```text
http://127.0.0.1:8000
```

## 3. Run Frontend

Open a second terminal:

```bash
cd evolviq_app
streamlit run frontend/app.py
```

## 4. Demo Flow

1. Go to **Research Mode**
2. Enter topic: `Behavioral Economics`
3. Click **Start Research**
4. Review synthesis, created knowledge, memory, and graph
5. Go to **Knowledge Chat**
6. Ask: `What do we know about loss aversion?`
7. Review evidence trace and graph relationships
8. Upload a PDF/DOCX/XLSX/TXT file
9. Process upload
10. Ask another contextual question
11. Check **Memory** and **Knowledge Graph** again

## 5. Architecture

```text
Streamlit UI
   ↓
FastAPI Backend
   ↓
Research / Upload / Chat Workflows
   ↓
SQLite Metadata + Memory
NetworkX Knowledge Graph
Evidence Store
```

## 6. Knowledge Types

The MVP stores:

- Facts
- Insights
- Entities
- Evidence
- Sources
- Memory records
- Graph relationships

## 7. Current Limitations

- Web research uses deterministic seed URLs for demo reliability.
- Extraction is heuristic, not full LLM-based yet.
- Contradiction detection is basic signal-based logic.
- Knowledge graph uses NetworkX JSON instead of Neo4j for easy local setup.
- Image/audio/video/YouTube processing is not fully implemented in this MVP.

## 8. Future Improvements

- Add OpenAI/Claude extraction pipeline
- Add Tavily/SerpAPI search
- Add Neo4j production graph
- Add Chroma/Qdrant vector retrieval
- Add Whisper for audio/video
- Add YouTube transcript ingestion
- Add graph visualization
- Add stronger confidence scoring
- Add source quality ranking
- Add incremental re-indexing jobs
```
