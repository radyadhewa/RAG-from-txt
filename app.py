import streamlit as st
import ollama
from base_rag import load_vector_db, retrieve, LANGUAGE_MODEL

# Load vector DB
VECTOR_DB = load_vector_db()

st.set_page_config(page_title="SI Chatbot", layout="wide")

# Display logo and title
col1, col2 = st.columns([1, 8])
with col1:
    st.image("assets\SISFO TELU.png", width=70)
with col2:
    st.title("💬 Chatbot RAG - Tanya jawab sama bot SI!")

# Session state for history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Input form
with st.form("chat_input", clear_on_submit=True):
    user_input = st.text_input("Pertanyaan hari ini:", placeholder="Type your question here...")
    submitted = st.form_submit_button("Tanya")

# On submit
if submitted and user_input:
    # Retrieve relevant knowledge
    retrieved = retrieve(user_input, VECTOR_DB)
    chunks = "\n".join([f"- {chunk.strip()}" for chunk, _ in retrieved])

    # Create prompt
    prompt = f"""You are a helpful chatbot.
Use only the following pieces of context to answer the question. Don't make up any new information:
{chunks}
"""

    # Build message history
    messages = [{"role": "system", "content": prompt}]
    messages += st.session_state.chat_history
    messages.append({"role": "user", "content": user_input})

    # Generate reply
    bot_reply = ""
    stream = ollama.chat(model=LANGUAGE_MODEL, messages=messages, stream=True)
    for chunk in stream:
        bot_reply += chunk["message"]["content"]

    # Save history
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})

# Display chat
for msg in st.session_state.chat_history:
    role = "Pak Taufik Bot" if msg["role"] == "assistant" else "Mahasiswa Banyak Tanya"
    with st.chat_message(role):
        st.markdown(msg["content"])