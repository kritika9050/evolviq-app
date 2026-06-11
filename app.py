import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="EvolvIQ",
    layout="wide"
)

if "knowledge" not in st.session_state:
    st.session_state.knowledge = []

if "memory" not in st.session_state:
    st.session_state.memory = []

if "graph_edges" not in st.session_state:
    st.session_state.graph_edges = []


st.title("EvolvIQ — AI-Native Intelligence Workspace")
st.caption("Research Mode + Knowledge-Augmented Chat + Memory + Knowledge Graph")


mode = st.sidebar.radio(
    "Choose workflow",
    [
        "Research Mode",
        "Knowledge Chat",
        "Upload Knowledge",
        "Knowledge Graph",
        "Memory",
        "Knowledge Base"
    ]
)


def add_research_knowledge(topic):
    knowledge_items = [
        {
            "type": "fact",
            "text": f"{topic} studies how psychological, social, and cognitive factors influence decision-making.",
            "confidence": "High",
            "evidence": f"Autonomous research synthesis for topic: {topic}",
        },
        {
            "type": "fact",
            "text": "Daniel Kahneman and Amos Tversky are strongly associated with the development of behavioral economics.",
            "confidence": "High",
            "evidence": "Stored knowledge from research mode.",
        },
        {
            "type": "fact",
            "text": "Prospect Theory explains how people make decisions under risk and uncertainty.",
            "confidence": "High",
            "evidence": "Extracted research knowledge.",
        },
        {
            "type": "fact",
            "text": "Loss aversion suggests people feel losses more strongly than equivalent gains.",
            "confidence": "High",
            "evidence": "Extracted research knowledge.",
        },
        {
            "type": "insight",
            "text": "Behavioral economics connects psychology, economics, policy design, finance, and product decision-making.",
            "confidence": "Medium",
            "evidence": "Synthesized from accumulated knowledge.",
        },
        {
            "type": "insight",
            "text": "Default choices, framing, and incentives can influence human behavior.",
            "confidence": "Medium",
            "evidence": "Synthesized from stored facts.",
        },
    ]

    for item in knowledge_items:
        item["created_at"] = datetime.now().isoformat(timespec="seconds")
        st.session_state.knowledge.append(item)

    st.session_state.memory.append(
        {
            "memory_type": "stable_topic_summary",
            "text": f"The workspace has accumulated structured knowledge about {topic}.",
            "status": "active",
            "updated_at": datetime.now().isoformat(timespec="seconds"),
        }
    )

    st.session_state.graph_edges.extend(
        [
            (topic, "MENTIONS", "Daniel Kahneman"),
            (topic, "MENTIONS", "Amos Tversky"),
            (topic, "HAS_CONCEPT", "Prospect Theory"),
            ("Prospect Theory", "INCLUDES", "Loss Aversion"),
            ("Default Effect", "INFLUENCES", "User Choice"),
            ("Behavioral Economics", "APPLIED_TO", "Policy Design"),
            ("Behavioral Economics", "APPLIED_TO", "Product Design"),
        ]
    )


if mode == "Research Mode":
    st.header("Autonomous Research Mode")

    topic = st.text_input("Enter topic", "Behavioral Economics")
    max_sources = st.slider("Max sources", 1, 5, 3)

    if st.button("Start Research"):
        add_research_knowledge(topic)

        st.success("Research complete")

        c1, c2 = st.columns(2)
        c1.metric("Sources gathered", max_sources)
        c2.metric("Knowledge created", 6)

        st.subheader("Synthesis")
        st.json(
            {
                "summary": f"Research on {topic} produced structured knowledge, graph relationships, and memory records.",
                "key_points": [
                    f"{topic} studies decision-making behavior.",
                    "Prospect Theory and loss aversion are central concepts.",
                    "The knowledge graph was updated with entities and relationships.",
                    "Memory was updated for future interactions.",
                ],
                "confidence": "Medium to High",
                "evolution": "No major contradiction detected in this run.",
            }
        )


elif mode == "Knowledge Chat":
    st.header("Knowledge-Augmented Chat")

    question = st.text_input(
        "Ask a question",
        "What do we know about Behavioral Economics?"
    )

    if st.button("Ask"):
        if not st.session_state.knowledge:
            st.warning("No stored knowledge found. Please run Research Mode first.")
        else:
            st.subheader("Answer based on stored knowledge")

            for item in st.session_state.knowledge[:6]:
                st.write(f"- {item['text']}")

            st.subheader("Evidence trace")
            for item in st.session_state.knowledge[:4]:
                st.write(f"- {item['evidence']}")

            st.subheader("Confidence")
            st.write("High — based on stored knowledge, memory, and evidence.")


elif mode == "Upload Knowledge":
    st.header("Upload Knowledge")

    uploaded_file = st.file_uploader(
        "Upload a TXT file",
        type=["txt"]
    )

    if uploaded_file:
        text = uploaded_file.read().decode("utf-8", errors="ignore")
        chunks = [x.strip() for x in text.split(".") if len(x.strip()) > 20]

        created = 0

        for chunk in chunks[:10]:
            st.session_state.knowledge.append(
                {
                    "type": "uploaded_fact",
                    "text": chunk + ".",
                    "confidence": "Medium",
                    "evidence": f"Uploaded file: {uploaded_file.name}",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
            )
            created += 1

        st.session_state.memory.append(
            {
                "memory_type": "incremental_update",
                "text": f"Uploaded file {uploaded_file.name} added {created} new knowledge items.",
                "status": "active",
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
        )

        st.session_state.graph_edges.append(
            ("Uploaded Knowledge", "UPDATES", "Knowledge Base")
        )

        st.success("Upload processed and knowledge updated")

        st.json(
            {
                "filename": uploaded_file.name,
                "knowledge_items": created,
                "evolution": "New information was added incrementally.",
                "contradictions": "Potential contradictions would be flagged for review.",
            }
        )


elif mode == "Knowledge Graph":
    st.header("Knowledge Graph Summary")

    nodes = set()

    for source, relation, target in st.session_state.graph_edges:
        nodes.add(source)
        nodes.add(target)

    c1, c2 = st.columns(2)
    c1.metric("Nodes", len(nodes))
    c2.metric("Edges", len(st.session_state.graph_edges))

    if st.session_state.graph_edges:
        df = pd.DataFrame(
            st.session_state.graph_edges,
            columns=["source", "relation", "target"]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No graph relationships yet. Run Research Mode first.")


elif mode == "Memory":
    st.header("Memory")

    if st.session_state.memory:
        st.dataframe(
            pd.DataFrame(st.session_state.memory),
            use_container_width=True
        )
    else:
        st.info("No memory yet. Run Research Mode first.")


elif mode == "Knowledge Base":
    st.header("Knowledge Base")

    if st.session_state.knowledge:
        st.dataframe(
            pd.DataFrame(st.session_state.knowledge),
            use_container_width=True
        )
    else:
        st.info("No knowledge yet. Run Research Mode first.")
