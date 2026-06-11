import requests
import uuid
from .extractors import html_to_text

SEED_URLS = {
    "behavioral economics": [
        "https://en.wikipedia.org/wiki/Behavioral_economics",
        "https://en.wikipedia.org/wiki/Prospect_theory"
    ],
    "urban planning": ["https://en.wikipedia.org/wiki/Urban_planning"],
    "space exploration": ["https://en.wikipedia.org/wiki/Space_exploration"],
    "climate change": ["https://en.wikipedia.org/wiki/Climate_change"],
    "psychology": ["https://en.wikipedia.org/wiki/Psychology"],
    "chocolate manufacturing": ["https://en.wikipedia.org/wiki/Chocolate"]
}


def gather_sources(topic: str, max_sources: int = 5):
    # MVP: deterministic seed sources. Replace with Tavily/SerpAPI for full web search.
    urls = SEED_URLS.get(topic.lower(), [f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"])
    out = []
    for url in urls[:max_sources]:
        try:
            r = requests.get(url, timeout=12, headers={"User-Agent": "EvolvIQ-MVP/1.0"})
            text = html_to_text(r.text)
            if len(text) < 300:
                continue
            title = url.split("/")[-1].replace("_", " ")
            out.append({"id": f"src_{uuid.uuid4().hex[:10]}", "title": title, "url": url, "source_type": "url", "text": text[:25000]})
        except Exception:
            continue
    return out
