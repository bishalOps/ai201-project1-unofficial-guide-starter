"""
app.py  — The Unofficial CS Career Guide (Streamlit UI)

Run with:
    streamlit run app.py
Then open http://localhost:8501
"""

import os
import streamlit as st
from embed import build_index, CHROMA_PATH
from rag import ask

st.set_page_config(page_title="The Unofficial CS Career Guide", page_icon="💼")
st.title("💼 The Unofficial CS Career Guide")
st.caption(
    "Ask anything about CS internships, coding interviews, resumes, "
    "salary negotiation, or early career advice. Answers come only from "
    "real Reddit threads — not the model's general knowledge."
)

# Build the search index on first run (skipped once chroma_db/ exists).
if not os.path.exists(CHROMA_PATH):
    with st.spinner("Building search index (one-time setup, ~30s)..."):
        build_index()
    st.success("Index built!")

st.divider()

with st.expander("Example questions"):
    st.markdown(
        "- How early should I start applying for summer internships?\n"
        "- Is Leetcode enough to prepare for FAANG interviews?\n"
        "- How do I negotiate a return offer without damaging the relationship?\n"
        "- What side projects actually help a CS resume?\n"
        "- What should I do in my first week as an intern?"
    )

question = st.text_input(
    "Your question",
    placeholder="e.g. What do I do if I fail a coding interview?",
)

if st.button("Ask", type="primary") and question.strip():
    with st.spinner("Searching documents and generating answer..."):
        result = ask(question, k=5)

    st.markdown("### Answer")
    st.markdown(result["answer"])

    if result["sources"]:
        st.markdown("**Sources**")
        st.markdown("\n".join(f"- `{s}`" for s in result["sources"]))

    with st.expander("Retrieved context chunks"):
        for i, chunk in enumerate(result["chunks"], 1):
            st.markdown(
                f"**[{i}] {chunk['filename']}** "
                f"(chunk #{chunk['chunk_index']}, distance {chunk['distance']:.3f})"
            )
            st.text(chunk["text"][:400])
            st.divider()
