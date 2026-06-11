from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil, uuid, json
from . import db
from .research import gather_sources
from .knowledge import extract_knowledge_from_text, update_memory_from_items, detect_simple_contradictions
from .extractors import extract_from_file
from .graph_store import update_graph, graph_summary, neighborhood
from .models import ResearchRequest, ChatRequest

BASE_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = BASE_DIR / "storage" / "uploads"

app = FastAPI(title="EvolvIQ Intelligence Workspace")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    db.init_db()
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
def root():
    return {"app": "EvolvIQ", "status": "running"}

@app.post("/research")
def research(req: ResearchRequest):
    sources = gather_sources(req.topic, req.max_sources)
    created, reinforced, contradictions = [], [], []
    for source in sources:
        db.insert_source(source)
        items, evidence, entities = extract_knowledge_from_text(req.topic, source["id"], source["text"])
        existing = db.list_knowledge(300)
        for ev in evidence:
            db.insert_evidence(ev)
        saved_ids = []
        for item in items:
            contradictions.extend(detect_simple_contradictions(item["text"], existing))
            kid, action = db.insert_knowledge(item)
            saved_ids.append(kid)
            created.append(item) if action == "created" else reinforced.append(item)
        update_graph(req.topic, source, items, entities)
        update_memory_from_items(req.topic, saved_ids)
    synthesis = synthesize(req.topic, created, reinforced, contradictions)
    return {"topic": req.topic, "sources_gathered": len(sources), "knowledge_created": len(created), "reinforced": len(reinforced), "contradictions": contradictions[:5], "synthesis": synthesis}

@app.post("/upload")
def upload(file: UploadFile = File(...), topic: str = "Uploaded Knowledge"):
    dest = UPLOAD_DIR / f"{uuid.uuid4().hex}_{file.filename}"
    with dest.open("wb") as f:
        shutil.copyfileobj(file.file, f)
    text = extract_from_file(str(dest))
    source = {"id": f"src_{uuid.uuid4().hex[:10]}", "title": file.filename, "url": None, "source_type": "upload", "text": text[:25000]}
    db.insert_source(source)
    items, evidence, entities = extract_knowledge_from_text(topic, source["id"], text)
    existing = db.list_knowledge(300)
    contradictions = []
    ids = []
    for ev in evidence:
        db.insert_evidence(ev)
    for item in items:
        contradictions.extend(detect_simple_contradictions(item["text"], existing))
        kid, _ = db.insert_knowledge(item)
        ids.append(kid)
    update_graph(topic, source, items, entities)
    update_memory_from_items(topic, ids)
    return {"filename": file.filename, "characters_processed": len(text), "knowledge_items": len(items), "contradictions": contradictions[:5]}

@app.post("/chat")
def chat(req: ChatRequest):
    knowledge = db.list_knowledge(200)
    q_words = set(req.question.lower().split())
    scored = []
    for k in knowledge:
        words = set(k["text"].lower().split())
        score = len(q_words.intersection(words))
        if score > 0:
            scored.append((score, k))
    top = [k for _, k in sorted(scored, key=lambda x: x[0], reverse=True)[:6]]
    evidence_ids = []
    for k in top:
        try:
            evidence_ids += json.loads(k.get("evidence_ids") or "[]")
        except Exception:
            pass
    evidence = db.get_evidence(evidence_ids[:10])
    rels = neighborhood(req.question)
    answer = grounded_answer(req.question, top, evidence, rels)
    return {"answer": answer, "knowledge_used": top, "evidence": evidence, "relationships": rels, "confidence": confidence_label(top, evidence)}

@app.get("/knowledge")
def knowledge():
    return {"knowledge": db.list_knowledge(300)}

@app.get("/memory")
def memory():
    return {"memory": db.list_memory()}

@app.get("/graph")
def graph():
    return graph_summary()


def synthesize(topic, created, reinforced, contradictions):
    bullets = [x["text"] for x in created[:5]]
    return {
        "summary": f"Research on {topic} produced {len(created)} new knowledge items and reinforced {len(reinforced)} existing items.",
        "key_points": bullets,
        "evolution": "Contradictions detected and flagged." if contradictions else "No strong contradiction detected in this run.",
        "confidence": "Medium — MVP uses heuristic extraction; evidence is preserved for traceability."
    }


def grounded_answer(question, top, evidence, rels):
    if not top:
        return "I do not have enough stored knowledge yet. Run Research Mode or upload a source first."
    facts = "\n".join(f"- {k['text']}" for k in top[:5])
    ev = "\n".join(f"- {e['excerpt'][:220]}..." for e in evidence[:4])
    rel = "\n".join(f"- {r['source']} → {r['relation']} → {r['target']}" for r in rels[:5]) or "- No direct graph relationships found for this query."
    return f"Answer based on stored knowledge:\n{facts}\n\nEvidence trace:\n{ev}\n\nGraph relationships:\n{rel}"


def confidence_label(top, evidence):
    if len(top) >= 5 and len(evidence) >= 4:
        return "High"
    if len(top) >= 2:
        return "Medium"
    return "Low"
