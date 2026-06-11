from pathlib import Path
import json
import networkx as nx

BASE_DIR = Path(__file__).resolve().parents[1]
GRAPH_PATH = BASE_DIR / "storage" / "knowledge_graph.json"


def load_graph():
    g = nx.DiGraph()
    if GRAPH_PATH.exists():
        data = json.loads(GRAPH_PATH.read_text())
        g = nx.node_link_graph(data, directed=True)
    return g


def save_graph(g):
    GRAPH_PATH.parent.mkdir(parents=True, exist_ok=True)
    GRAPH_PATH.write_text(json.dumps(nx.node_link_data(g), indent=2))


def update_graph(topic, source, knowledge_items, entities):
    g = load_graph()
    topic_id = f"topic:{topic.lower()}"
    source_id = f"source:{source['id']}"
    g.add_node(topic_id, label=topic, type="Topic")
    g.add_node(source_id, label=source["title"], type="Source", url=source.get("url"))
    g.add_edge(topic_id, source_id, relation="RESEARCHED_FROM")

    for entity in entities:
        ent_id = f"entity:{entity.lower()}"
        g.add_node(ent_id, label=entity, type="Entity")
        g.add_edge(topic_id, ent_id, relation="MENTIONS")

    for k in knowledge_items:
        kid = f"knowledge:{k['id']}"
        g.add_node(kid, label=k["text"][:80], type=k["type"], confidence=k.get("confidence", 0.5), status=k.get("status", "active"))
        g.add_edge(topic_id, kid, relation="HAS_KNOWLEDGE")
        g.add_edge(kid, source_id, relation="SUPPORTED_BY")
        for entity in k.get("entities", []):
            ent_id = f"entity:{entity.lower()}"
            g.add_edge(kid, ent_id, relation="ABOUT")
    save_graph(g)


def graph_summary():
    g = load_graph()
    rels = []
    for u, v, d in g.edges(data=True):
        rels.append({
            "source": g.nodes[u].get("label", u),
            "relation": d.get("relation"),
            "target": g.nodes[v].get("label", v)
        })
    return {
        "nodes": g.number_of_nodes(),
        "edges": g.number_of_edges(),
        "relationships": rels[:200]
    }


def neighborhood(query: str):
    g = load_graph()
    query_l = query.lower()
    matches = [n for n, data in g.nodes(data=True) if query_l in str(data.get("label", "")).lower()]
    rows = []
    for n in matches[:10]:
        for _, v, d in g.out_edges(n, data=True):
            rows.append({"source": g.nodes[n].get("label", n), "relation": d.get("relation"), "target": g.nodes[v].get("label", v)})
        for u, _, d in g.in_edges(n, data=True):
            rows.append({"source": g.nodes[u].get("label", u), "relation": d.get("relation"), "target": g.nodes[n].get("label", n)})
    return rows[:100]
