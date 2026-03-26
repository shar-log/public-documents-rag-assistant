import streamlit as st
from chatbot import get_answer
from datetime import datetime
import os

# -----------------------------
# ✅ CONFIG
# -----------------------------
st.set_page_config(page_title="Legal RAG Assistant", layout="wide")

st.title("📘 Legal RAG Assistant")

# -----------------------------
# ✅ FILE PATH FOR FEEDBACK
# -----------------------------
FEEDBACK_FILE = os.path.join(os.getcwd(), "feedback.txt")

# -----------------------------
# ✅ INIT SESSION STATE
# -----------------------------
if "history" not in st.session_state:
    st.session_state.history = []

# -----------------------------
# ✅ INPUT FORM (prevents duplication)
# -----------------------------
with st.form("chat_form", clear_on_submit=True):
    query = st.text_input("Ask your legal question:")
    submitted = st.form_submit_button("Submit")

# -----------------------------
# ✅ HANDLE INPUT
# -----------------------------
if submitted and query:
    answer = get_answer(query)

    # prevent duplicate consecutive entries
    if not st.session_state.history or st.session_state.history[-1][0] != query:
        st.session_state.history.append((query, answer))

# -----------------------------
# ✅ DISPLAY CHAT (LATEST FIRST)
# -----------------------------
st.subheader("Chat History")

for i, (q, a) in enumerate(reversed(st.session_state.history)):
    idx = len(st.session_state.history) - 1 - i

    st.markdown(f"**You:** {q}")
    st.markdown(f"**Assistant:** {a}")

    # -----------------------------
    # ✅ FEEDBACK SECTION
    # -----------------------------
    st.markdown("**Do you like this response?**")

    col1, col2, col3 = st.columns([1, 1, 8])

    with col1:
        if st.button("👍", key=f"up_{idx}"):
            with open(FEEDBACK_FILE, "a") as f:
                f.write(f"{datetime.now()} | GOOD | Q: {q} | A: {a}\n")
            st.success("Feedback saved 👍")

    with col2:
        if st.button("👎", key=f"down_{idx}"):
            with open(FEEDBACK_FILE, "a") as f:
                f.write(f"{datetime.now()} | BAD | Q: {q} | A: {a}\n")
            st.warning("Feedback saved 👎")

    st.markdown("---")

# -----------------------------
# ✅ CLEAR CHAT BUTTON
# -----------------------------
if st.button("🧹 Clear Chat"):
    st.session_state.history = []