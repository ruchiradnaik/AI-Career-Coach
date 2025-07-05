from fpdf import FPDF
import datetime
import re

def remove_emojis(text):
    """
    Remove emojis and non-latin-1 characters for PDF compatibility.
    """
    return re.sub(r'[^\x00-\xff]', '', text)
    


def export_career_report(filename, user_name, resume_data, jd_skills, score_data, llm_feedback, projects):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "AI Career Coach Report", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)

    # Resume Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resume Summary", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, f"Name: {user_name or 'N/A'}")
    pdf.multi_cell(0, 8, f"Email: {resume_data.get('email', 'N/A')}")
    pdf.multi_cell(0, 8, f"Skills: {', '.join(resume_data.get('skills', [])) or 'N/A'}")
    pdf.ln(5)

    # JD Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Job Description Keywords", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, ", ".join(jd_skills) or 'N/A')
    pdf.ln(5)

    # Score Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Resume Fit Score", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, f"Score: {score_data['score']} / 100")
    pdf.multi_cell(0, 8, f"Fit Level: {score_data['fit_level']}")
    pdf.multi_cell(0, 8, f"Matched Skills: {', '.join(score_data['matched']) or 'N/A'}")
    pdf.multi_cell(0, 8, f"Missing Skills: {', '.join(score_data['missing']) or 'N/A'}")
    pdf.ln(5)

    # AI Feedback
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "AI Career Coach Feedback", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 8, llm_feedback or "N/A")
    pdf.ln(5)

    # Project Suggestions (Optional)
    if projects:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "Suggested Projects", ln=True)
        pdf.set_font("Arial", '', 12)
        for project in projects:
            pdf.multi_cell(0, 8, f" {project}")
        pdf.ln(5)

    # Save
    pdf.output(filename)
