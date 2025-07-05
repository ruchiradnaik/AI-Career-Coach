import streamlit as st
import os
import json
import tempfile
from resume_parser import extract_text_from_pdf, extract_links_from_pdf, preprocess_resume_text
from job_parser import extract_keywords_from_jd, compare_resume_to_jd
from chatbot import ask_career_question, improve_resume_lines, ask_career_question_multi_turn
from scoring import calculate_resume_score
from report_exporter import export_career_report
import warnings
from datetime import datetime

warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

st.set_page_config(page_title="AI Career Coach", page_icon="🧠")

# ------------------ INIT SESSION FLAGS ------------------
defaults = {
    "jd_skills": [],
    "feedback_requested": False,
    "project_requested": False,
    "score_requested": False,
    "rewrite_requested": False,
    "score_data": {},
    "explanation": "",
    "project_list": [],
    "improved_lines": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------------ CHAT MEMORY ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful AI career coach. Be clear, concise, and specific."}
    ]

# ------------------ RESUME UPLOAD ------------------
st.title("📄 Upload Your Resume")
st.write("Let the AI Career Coach read your resume and extract key details!")

uploaded_file = st.file_uploader("Choose your resume (PDF)", type="pdf")

resume_skills, raw_text, structured_info = [], "", {}

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_path = temp_file.name

    st.info("🔍 Extracting information...")
    raw_text = extract_text_from_pdf(temp_path)
    links = extract_links_from_pdf(temp_path)
    structured_info = preprocess_resume_text(raw_text, links)
    resume_skills = structured_info.get("skills", [])

    st.subheader("✅ Extracted Resume Summary")
    for key, value in structured_info.items():
        st.markdown(f"**{key.capitalize()}**: {value if value else '❌ Not found'}")

    base_name = os.path.splitext(uploaded_file.name)[0]
    output_dir = "data/parsed_resumes"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{base_name}_structured.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(structured_info, f, indent=2)

    st.success(f"📁 Structured resume saved to `{output_path}`")

# ------------------ JOB DESCRIPTION INPUT ------------------
st.subheader("📥 Paste a Job Description")
jd_input = st.text_area("Paste the job description here:")

if jd_input and uploaded_file:
    if st.button("🔍 Extract JD Skills"):
        st.session_state.jd_skills = extract_keywords_from_jd(jd_input)
        st.success("✅ JD Skills Extracted")
        st.write(st.session_state.jd_skills)

    if resume_skills:
        comparison = compare_resume_to_jd(resume_skills, st.session_state.jd_skills)
        
        st.subheader("📊 Resume ↔ JD Skill Matching")
        st.markdown(f"✅ **Matched Skills:** {', '.join(comparison['matched_skills']) or 'None'}")
        st.markdown(f"❌ **Missing Skills:** {', '.join(comparison['missing_skills']) or 'None'}")

        if comparison["suggestions"]:
            st.subheader("🧠 Career Suggestions")
            for tip in comparison["suggestions"]:
                st.info(tip)


jd_skills = st.session_state.jd_skills

# ------------------ INDEPENDENT BUTTONS ------------------
st.subheader("📌 AI Actions")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📈 Resume Score"):
        st.session_state.score_requested = True
        st.session_state.feedback_requested = False
        st.session_state.project_requested = False
        st.session_state.rewrite_requested = False

with col2:
    if st.button("🧠 Feedback"):
        st.session_state.feedback_requested = True
        st.session_state.score_requested = False
        st.session_state.project_requested = False
        st.session_state.rewrite_requested = False

with col3:
    if st.button("💡 Project Ideas"):
        st.session_state.project_requested = True
        st.session_state.score_requested = False
        st.session_state.feedback_requested = False
        st.session_state.rewrite_requested = False

with col4:
    if st.button("✍️ Resume Suggestions"):
        st.session_state.rewrite_requested = True
        st.session_state.project_requested = False
        st.session_state.feedback_requested = False
        st.session_state.score_requested = False

# ------------------ EXECUTION BLOCKS ------------------

if st.session_state.score_requested and resume_skills and jd_skills:
    st.session_state.score_data = calculate_resume_score(resume_skills, jd_skills)
    score_data = st.session_state.score_data

    st.subheader("📈 Resume Fit Score")
    st.progress(score_data["score"] / 100)
    st.markdown(f"""
**Score:** {score_data['score']} / 100  
**Fit Level:** {score_data['fit_level']}  
✅ **Matched Skills:** {', '.join(score_data['matched']) or 'None'}  
❌ **Missing Skills:** {', '.join(score_data['missing']) or 'None'}  
""")

if st.session_state.feedback_requested and resume_skills and jd_skills:
    st.subheader("🧠 AI Coach Feedback")
    with st.spinner("Thinking..."):
        st.session_state.explanation = ask_career_question(
            "Explain this resume score and how to improve.",
            {"skills": resume_skills},
            jd_skills
        )
        st.write(st.session_state.explanation)

if st.session_state.project_requested and resume_skills and jd_skills:
    st.subheader("💡 AI Suggested Projects")
    score_data = st.session_state.score_data or calculate_resume_score(resume_skills, jd_skills)
    st.session_state.score_data = score_data

    if score_data["missing"]:
        with st.spinner("Thinking of projects just for you..."):
            project_prompt = f"""
The user's resume is missing the following skills: {', '.join(score_data['missing'])}.
Suggest 2-3 smart, resume-boosting project ideas that would help them demonstrate these skills.
Each project should include:
- a short title
- 1-2 line description
- clearly target the missing skills
"""
            project_ideas = ask_career_question(project_prompt, structured_info, jd_skills)
            st.write(project_ideas)
            st.session_state.project_list = [line.strip("\n ") for line in project_ideas.splitlines() if line.strip()]
    else:
        st.success("✅ No missing skills! Your resume already covers all required areas.")

if st.session_state.rewrite_requested and raw_text:
    st.subheader("✍️ Resume Improvement Suggestions")
    with st.spinner("Analyzing your resume..."):
        st.session_state.improved_lines = improve_resume_lines(raw_text)
        for original, improved_line in st.session_state.improved_lines:
            st.markdown(f"""
**📌 Original:**  
> {original}

**✅ Improved:**  
> {improved_line}
---
""")

# ------------------ CHATBOT ------------------
from datetime import datetime

def handle_user_message():
    user_input = st.session_state.user_input
    if not user_input.strip():
        return

    now = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input,
        "time": now
    })

    # Provide resume + JD context ONLY to the LLM, NOT as visible chat messages
    resume_context = "\n".join([f"{k}: {v}" for k, v in structured_info.items()])
    jd_context = ", ".join(st.session_state.jd_skills) if st.session_state.jd_skills else "N/A"

    prompt_context = [
        {"role": "system", "content": "You are a helpful AI career coach."},
        {"role": "user", "content": f"Resume:\n{resume_context}\n\nJD Keywords:\n{jd_context}"}
    ] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history
    ]

    response = ask_career_question_multi_turn(prompt_context)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "time": now
    })

    st.session_state.user_input = ""


# ---------- CHAT SIDEBAR ----------
st.sidebar.title("💬 AI Career Coach Chat")

# Clear chat
if st.sidebar.button("🧹 Clear Chat"):
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful AI career coach."}
    ]

# Show chat history (skip system prompt)
for msg in st.session_state.chat_history[1:]:
    role = "🧑 You" if msg["role"] == "user" else "🤖 Coach"
    time = msg.get("time", "--:--")
    st.sidebar.markdown(f"**{role}** [{time}]")
    st.sidebar.markdown(f"> {msg['content']}")
    st.sidebar.markdown("---")

# Chat input
st.sidebar.text_input(
    "Ask a question...",
    key="user_input",
    on_change=handle_user_message
)

with st.sidebar.expander("💾 Save Chat"):
    chat_name = st.text_input("Chat title:")
    if st.button("Save Chat"):
        if chat_name:
            path = f"chat_sessions/{chat_name}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(st.session_state.chat_history, f, indent=2)
            st.success(f"✅ Saved as `{chat_name}.json`")

saved_chats = [f.replace(".json", "") for f in os.listdir("chat_sessions") if f.endswith(".json")]

with st.sidebar.expander("📂 Load Previous Chat"):
    selected_chat = st.selectbox("Choose a chat", ["-- Select --"] + saved_chats)

    if selected_chat != "-- Select --":
        with open(f"chat_sessions/{selected_chat}.json", "r", encoding="utf-8") as f:
            st.session_state.chat_history = json.load(f)
        st.success(f"✅ Loaded `{selected_chat}`")




# ------------------ REPORT EXPORT ------------------
st.subheader("📥 Download Career Report")

if st.button("📄 Generate PDF Report"):
    score_data = st.session_state.get("score_data", {
        "score": 0,
        "fit_level": "Not generated",
        "matched": [],
        "missing": []
    })
    explanation = st.session_state.get("explanation", "No feedback generated.")
    project_list = st.session_state.get("project_list", [])

    filename = f"career_report_{base_name}.pdf"
    export_career_report(
        filename=filename,
        user_name=base_name,
        resume_data=structured_info,
        jd_skills=jd_skills,
        score_data=score_data,
        llm_feedback=explanation,
        projects=project_list
    )
    with open(filename, "rb") as f:
        st.download_button(
            label="Download Report",
            data=f,
            file_name=filename,
            mime="application/pdf"
        )
