from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ResearchRequest(BaseModel):
    topic: str
    max_sources: int = 5

class ChatRequest(BaseModel):
    question: str
    use_web: bool = False

class KnowledgeItem(BaseModel):
    id: str
    type: str
    text: str
    entities: List[str] = []
    confidence: float = 0.5
    status: str = "active"
    evidence_ids: List[str] = []
    metadata: Dict[str, Any] = {}

class SourceRecord(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    source_type: str
    text: str
