import os  
import requests
import streamlit as st
from vector_store import build_faiss_index, search_index, get_top_k_chunks
from utils import split_text_into_chunks

# === Groq Configuration ===
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]  # Set in secrets.toml or Streamlit Cloud
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.1-8b-instant"

# === Groq Chat Caller ===
def call_groq_chat(messages, model=GROQ_MODEL, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        st.error(f"Groq API Error: {response.status_code} - {response.text}")
        return "⚠️ Sorry, something went wrong with the AI response."


# === 1. RAG-style Career Question Answering ===
def ask_career_question(question, resume_data, jd_skills):
    resume_str = "\n".join([f"{k}: {v}" for k, v in resume_data.items() if v])
    jd_str = ", ".join(jd_skills)

    # Chunk and index resume + JD
    combined_text = resume_str + "\n\nJob Description:\n" + jd_str
    chunks = split_text_into_chunks(combined_text)
    index, _ = build_faiss_index(chunks)

    # Retrieve top matching chunks based on the question
    top_chunks = search_index(question, index, chunks)
    context = "\n".join(top_chunks)

    prompt = f"""
Use the following context to answer the user's career question:

{context}

User Question:
\"\"\"{question}\"\"\"
"""

    messages = [
        {"role": "system", "content": "You are a helpful AI career coach."},
        {"role": "user", "content": prompt}
    ]

    return call_groq_chat(messages)


# === 2. Resume Line Improver ===
def improve_resume_lines(resume_text, k=3):
    """
    Use RAG to improve 2-3 lines from the resume with better phrasing.
    """
    chunks = resume_text.split('\n')
    chunks = [c.strip() for c in chunks if c.strip()]

    index, all_chunks = build_faiss_index(chunks)

    target_lines = chunks[:3]  # You can enhance this with NLP logic

    improved_lines = []

    for line in target_lines:
        related_chunks = get_top_k_chunks(index, chunks, line, k=k)
        context = "\n".join(related_chunks)

        prompt = f"""
You are a professional resume editor.

Original resume line:
"{line}"

Relevant resume context:
{context}

Rewrite this line to be more impactful using:
- Action verbs
- Measurable outcomes
- Resume best practices

Return only the improved line.
"""

        improved = ask_career_question(prompt, {}, [])
        improved_lines.append((line, improved))

    return improved_lines


# === 3. Multi-turn Memory Chat ===
def ask_career_question_multi_turn(chat_history):
    return call_groq_chat(chat_history)
