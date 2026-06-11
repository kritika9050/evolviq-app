import hashlib
import re
import uuid
import json
from collections import Counter
from . import db

STOPWORDS = set('''the a an and or of to in for with by on at from is are was were be been being this that as into it its their his her has have had can may should about between over under more most less than also'''.split())


def stable_id(prefix: str, text: str) -> str:
    return f"{prefix}_{hashlib.sha1(text.encode('utf-8')).hexdigest()[:12]}"


def extract_entities(text: str, max_entities=20):
    candidates = re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3}\b", text)
    filtered = [c.strip() for c in candidates if c.lower() not in STOPWORDS and len(c) > 2]
    return [x for x, _ in Counter(filtered).most_common(max_entities)]


def sentence_score(sentence: str, topic: str):
    words = [w.lower() for w in re.findall(r"\w+", sentence)]
    topic_words = set(topic.lower().split())
    score = len(topic_words.intersection(words)) + min(len(words) / 30, 2)
    if any(k in sentence.lower() for k in ["because", "leads to", "causes", "associated with", "evidence", "study", "risk", "impact"]):
        score += 1.5
    return score


def extract_knowledge_from_text(topic: str, source_id: str, text: str):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    ranked = sorted([s.strip() for s in sentences if len(s.strip()) > 60], key=lambda s: sentence_score(s, topic), reverse=True)
    selected = ranked[:12]
    all_entities = extract_entities(text)
    items = []
    evidence = []
    for s in selected:
        ev_id = stable_id("ev", source_id + s[:120])
        evidence.append({"id": ev_id, "source_id": source_id, "excerpt": s[:800], "page_or_location": "text"})
        ktype = "insight" if any(w in s.lower() for w in ["suggest", "indicate", "pattern", "risk", "impact"]) else "fact"
        entities = [e for e in all_entities if e in s][:5]
        items.append({
            "id": stable_id("k", s),
            "type": ktype,
            "text": s,
            "entities": entities,
            "confidence": 0.68 if ktype == "fact" else 0.58,
            "status": "active",
            "evidence_ids": [ev_id],
            "metadata": {"topic": topic}
        })
    return items, evidence, all_entities


def detect_simple_contradictions(new_text: str, existing_items):
    contradictions = []
    neg_markers = ["not", "no longer", "does not", "isn't", "cannot", "contrary"]
    for old in existing_items:
        old_text = old["text"]
        shared = set(re.findall(r"\w+", new_text.lower())).intersection(set(re.findall(r"\w+", old_text.lower())))
        if len(shared) >= 5:
            new_neg = any(m in new_text.lower() for m in neg_markers)
            old_neg = any(m in old_text.lower() for m in neg_markers)
            if new_neg != old_neg:
                contradictions.append({"old": old, "new_text": new_text, "reason": "Similar subject but opposite negation signal."})
    return contradictions


def update_memory_from_items(topic, knowledge_ids):
    db.add_memory({
        "id": stable_id("mem", topic),
        "memory_type": "stable_topic_summary",
        "text": f"The workspace has accumulated structured knowledge about {topic}.",
        "status": "active",
        "confidence": 0.75,
        "related_knowledge_ids": knowledge_ids,
        "change_note": "Updated after autonomous research/upload processing."
    })
