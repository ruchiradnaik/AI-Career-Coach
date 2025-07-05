import os
import PyPDF2
import json
import re
import fitz

def extract_links_from_pdf(pdf_path):
    """
    Extracts all URI hyperlinks from the PDF (e.g., LinkedIn, GitHub).
    """
    links = []
    doc = fitz.open(pdf_path)

    for page in doc:
        for link in page.get_links():
            uri = link.get("uri", None)
            if uri:
                links.append(uri)

    return links

def extract_text_from_pdf(pdf_path, save_as_json=True):
    """
    Extracts text from a PDF and optionally saves to a JSON file.
    
    Args:
        pdf_path (str): Path to the PDF file.
        save_as_json (bool): Whether to save output to JSON.
    
    Returns:
        str: Extracted text.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"File not found: {pdf_path}")

    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

    text = text.replace('\n', ' ').replace('\r', '').strip()

    if save_as_json:
        output_path = "data/parsed_resumes"
        os.makedirs(output_path, exist_ok=True)
        resume_filename = os.path.splitext(os.path.basename(pdf_path))[0]
        json_data = {
            "file_name": os.path.basename(pdf_path),
            "raw_text": text
        }
        output_file = os.path.join(output_path, f"{resume_filename}.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2)
        print(f"✅ Resume text saved as JSON to: {output_file}")

    return text

# Predefined list of common tech skills (expandable)
COMMON_SKILLS = [
    "python", "java", "c++", "sql", "excel", "power bi", "tableau",
    "tensorflow", "pytorch", "nlp", "opencv", "machine learning",
    "deep learning", "data analysis", "data science", "html", "css",
    "javascript", "flask", "django", "aws", "azure", "git"
]

def preprocess_resume_text(text, links = None):
    """
    Extracts structured fields from raw resume text.
    
    Args:
        text (str): Raw resume text.
    
    Returns:
        dict: Structured fields like email, phone, skills, etc.
    """
    data = {}

    # 1. Email
    email_match = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    data["email"] = email_match[0] if email_match else None

    # 2. Phone number (supports various formats)
    phone_match = re.findall(r'\+?\d[\d\s\-]{8,15}', text)
    data["phone"] = phone_match[0] if phone_match else None

      # 3. Extract LinkedIn & GitHub from real PDF hyperlinks
    if links:
        for link in links:
            if "linkedin.com" in link:
                data["linkedin"] = link
            if "github.com" in link:
                data["github"] = link

    # If no links found, fallback to old regex method (optional)


    # 5. Skills (case insensitive keyword match)
    found_skills = []
    for skill in COMMON_SKILLS:
        if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE):
            found_skills.append(skill.lower())
    data["skills"] = list(set(found_skills))  # Remove duplicates

    # 6. Education Section (basic heuristic)
    edu_match = re.search(r"(education|qualifications)(.*?)(experience|skills|projects|summary|$)", text, re.IGNORECASE | re.DOTALL)
    data["education"] = edu_match.group(2).strip() if edu_match else None

    # 7. Experience Section
    exp_match = re.search(
        r"(?:experience|work history)\s*(.*?)(?:education|skills|projects|summary|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    exp_text = exp_match.group(1).strip() if exp_match else None
    data["experience"] = exp_text if exp_text and len(exp_text) > 30 else None


    return data