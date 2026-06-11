import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:8000"
st.set_page_config(page_title="EvolvIQ", layout="wide")
st.title("EvolvIQ — AI-Native Intelligence Workspace")
st.caption("Research Mode + Knowledge-Augmented Chat + Memory + Knowledge Graph")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose workflow", ["Research Mode", "Knowledge Chat", "Upload Knowledge", "Knowledge Graph", "Memory", "Knowledge Base"])

if page == "Research Mode":
    st.header("Autonomous Research Mode")
    topic = st.text_input("Enter topic", value="Behavioral Economics")
    max_sources = st.slider("Max sources", 1, 5, 3)
    if st.button("Start Research", type="primary"):
        with st.spinner("Researching, cleansing, extracting knowledge, updating graph and memory..."):
            r = requests.post(f"{API}/research", json={"topic": topic, "max_sources": max_sources}, timeout=120)
        data = r.json()
        st.success("Research complete")
        c1, c2, c3 = st.columns(3)
        c1.metric("Sources gathered", data.get("sources_gathered", 0))
        c2.metric("Knowledge created", data.get("knowledge_created", 0))
        c3.metric("Reinforced", data.get("reinforced", 0))
        st.subheader("Synthesis")
        st.json(data.get("synthesis", {}))
        if data.get("contradictions"):
            st.subheader("Contradictions / Evolution Detected")
            st.json(data["contradictions"])

elif page == "Knowledge Chat":
    st.header("Knowledge-Augmented Chat")
    q = st.text_area("Ask a question", value="What do we know about loss aversion?")
    if st.button("Ask", type="primary"):
        r = requests.post(f"{API}/chat", json={"question": q}, timeout=60)
        data = r.json()
        st.subheader("Answer")
        st.text(data.get("answer", ""))
        st.subheader("Confidence")
        st.info(data.get("confidence"))
        with st.expander("Knowledge Used"):
            st.json(data.get("knowledge_used", []))
        with st.expander("Evidence Used"):
            st.json(data.get("evidence", []))
        with st.expander("Graph Relationships"):
            st.json(data.get("relationships", []))

elif page == "Upload Knowledge":
    st.header("Upload Additional Information")
    topic = st.text_input("Topic/context for this upload", value="Uploaded Knowledge")
    file = st.file_uploader("Upload PDF, DOCX, XLSX, TXT, or MD", type=["pdf", "docx", "xlsx", "txt", "md"])
    if file and st.button("Process Upload", type="primary"):
        files = {"file": (file.name, file.getvalue())}
        r = requests.post(f"{API}/upload", params={"topic": topic}, files=files, timeout=120)
        data = r.json()
        st.success("Upload processed and knowledge updated")
        st.json(data)

elif page == "Knowledge Graph":
    st.header("Knowledge Graph Summary")
    data = requests.get(f"{API}/graph").json()
    c1, c2 = st.columns(2)
    c1.metric("Nodes", data.get("nodes", 0))
    c2.metric("Edges", data.get("edges", 0))
    rels = data.get("relationships", [])
    if rels:
        st.dataframe(pd.DataFrame(rels), use_container_width=True)
    else:
        st.info("No graph yet. Run Research Mode first.")

elif page == "Memory":
    st.header("Memory")
    data = requests.get(f"{API}/memory").json().get("memory", [])
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("No memory yet.")

elif page == "Knowledge Base":
    st.header("Structured Knowledge")
    data = requests.get(f"{API}/knowledge").json().get("knowledge", [])
    if data:
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.info("No knowledge yet. Run Research Mode or upload a source.")
