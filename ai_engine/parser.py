import re
import pdfplumber
import PyPDF2


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from PDF using pdfplumber,
    falling back to PyPDF2 if needed.
    """
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

    except Exception as e:
        print(f"[PARSER WARNING] pdfplumber failed: {e}")

    # Fallback
    if not text.strip():
        try:
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)

                for page in reader.pages:
                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        except Exception as e:
            print(f"[PARSER ERROR] PyPDF2 failed: {e}")

    return text.strip()


def extract_email(text):
    """
    Extract email using regex.
    """
    pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

    match = re.search(pattern, text)

    return match.group(0) if match else None


def extract_phone(text):
    """
    Extract phone number using regex.
    """
    pattern = r'(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}?\)?[-.\s]?\d{3,4}[-.\s]?\d{4})'

    matches = re.findall(pattern, text)

    for match in matches:
        digits = re.sub(r'\D', '', match)

        if 8 <= len(digits) <= 15:
            return match.strip()

    return None


def extract_name(text):
    """
    Extract probable candidate name from top resume lines.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    for line in lines[:5]:

        # Skip contact info
        if '@' in line:
            continue

        if any(word in line.lower() for word in [
            'resume', 'curriculum', 'cv',
            'email', 'phone', 'portfolio'
        ]):
            continue

        words = line.split()

        # Typical name heuristic
        if 2 <= len(words) <= 4:

            if re.match(r'^[a-zA-Z\s\.\-]+$', line):
                return line.title()

    return "Job Seeker"


def parse_sections(text):
    """
    Extract common resume sections.
    """

    sections = {
        'education': '',
        'experience': '',
        'projects': '',
        'certifications': '',
        'skills': ''
    }

    headings = {
        'education': ['education', 'academic'],
        'experience': ['experience', 'work experience'],
        'projects': ['projects'],
        'certifications': ['certifications', 'certificates'],
        'skills': ['skills', 'technical skills']
    }

    lines = text.split('\n')

    found_headings = []

    for i, line in enumerate(lines):

        clean_line = line.strip().lower()

        for sec, patterns in headings.items():

            for pat in patterns:

                if pat in clean_line:
                    found_headings.append((i, sec))
                    break

    found_headings.sort()

    for idx, (line_idx, sec) in enumerate(found_headings):

        start = line_idx + 1

        end = (
            found_headings[idx + 1][0]
            if idx + 1 < len(found_headings)
            else len(lines)
        )

        section_text = "\n".join(lines[start:end]).strip()

        sections[sec] = section_text

    return sections


def parse_resume(pdf_path):
    """
    Complete resume parsing pipeline.
    """

    raw_text = extract_text_from_pdf(pdf_path)

    sections = parse_sections(raw_text)

    return {
        'parsed_text': raw_text,
        'name': extract_name(raw_text),
        'email': extract_email(raw_text),
        'phone': extract_phone(raw_text),
        'education': sections['education'],
        'experience': sections['experience'],
        'projects': sections['projects'],
        'certifications': sections['certifications'],
        'skills_section': sections['skills']
    }

