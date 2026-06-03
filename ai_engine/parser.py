import re
import pdfplumber
import PyPDF2
import spacy

# Load spaCy model for NLP preprocessing and NER name extraction
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    # Fallback to loading it after downloading, we will download it in the setup phase
    nlp = None

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file using pdfplumber, falling back to PyPDF2 if necessary.
    """
    text = ""
    # Try pdfplumber first
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[PARSER WARNING] pdfplumber failed: {e}. Trying PyPDF2...")
        
    # Fallback to PyPDF2 if pdfplumber returns nothing or fails
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
    Extracts email address from text using regex.
    """
    email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None

def extract_phone(text):
    """
    Extracts phone number from text using regex.
    Supports international and local formats.
    """
    # Pattern to match numbers with optional country code, spaces, hyphens, and parentheses
    phone_pattern = r'(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}?\)?[-.\s]?\d{3,4}[-.\s]?\d{4})'
    matches = re.findall(phone_pattern, text)
    for match in matches:
        # Filter out matches that are too short (like single dates or numbers)
        digits = re.sub(r'\D', '', match)
        if 8 <= len(digits) <= 15:
            return match.strip()
    return None

def extract_name(text):
    """
    Extracts the user's name from resume text.
    Uses spaCy NER Person check, with a regex and layout fallback.
    """
    global nlp
    if nlp is None:
        try:
            nlp = spacy.load("en_core_web_sm")
        except OSError:
            pass

    # Method 1: spaCy NER
    if nlp:
        doc = nlp(text[:500])  # Scan only the beginning of the resume
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Ensure the name does not contain newlines and is reasonably sized
                name = ent.text.strip().replace('\n', ' ')
                # Filter out garbage
                if len(name.split()) >= 2 and len(name.split()) <= 4:
                    return name

    # Method 2: Heuristic Fallback
    # Resumes usually have the name on the first or second non-empty line.
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:3]:
        # Exclude contact info or common section headers
        if '@' in line or any(k in line.lower() for k in ['resume', 'curriculum', 'cv', 'email', 'phone', 'portfolio']):
            continue
        # Name should be 2-4 words and mostly letters
        words = line.split()
        if 2 <= len(words) <= 4 and re.match(r'^[a-zA-Z\s\.\-\,]+$', line):
            return line
            
    return "Job Seeker"

def parse_sections(text):
    """
    Splits the resume text into logical sections based on common headings.
    """
    sections = {
        'education': '',
        'experience': '',
        'projects': '',
        'certifications': '',
        'skills': ''
    }
    
    headings = {
        'education': ['education', 'academic', 'studies', 'degree', 'qualification', 'educational background'],
        'experience': ['experience', 'work experience', 'professional experience', 'employment history', 'work history', 'career history'],
        'projects': ['projects', 'academic projects', 'personal projects', 'key projects', 'technical projects'],
        'certifications': ['certifications', 'certificates', 'licenses', 'accreditations', 'credentials'],
        'skills': ['skills', 'technical skills', 'core skills', 'technologies', 'expertise', 'competencies']
    }
    
    lines = text.split('\n')
    found_headings = []
    
    # Iterate line by line to identify heading matches
    for i, line in enumerate(lines):
        clean_line = line.strip().lower()
        if not clean_line:
            continue
        
        # Check if line matches any heading pattern (headings are short, e.g. <= 4 words)
        words = clean_line.split()
        if len(words) <= 4:
            for sec, patterns in headings.items():
                matched = False
                for pat in patterns:
                    # Match exact word or phrase boundary
                    if re.search(r'\b' + re.escape(pat) + r'\b', clean_line):
                        found_headings.append((i, sec, line))
                        matched = True
                        break
                if matched:
                    break
                    
    if not found_headings:
        # Fallback: simple text keyword splitting
        for sec, patterns in headings.items():
            for pat in patterns:
                match = re.search(r'\b' + re.escape(pat) + r'\b', text.lower())
                if match:
                    # Extract 1000 characters after the keyword as a rough estimation
                    start_idx = match.end()
                    sections[sec] = text[start_idx:start_idx+1000].strip()
                    break
        return sections
        
    # Sort headings by their line index
    found_headings.sort(key=lambda x: x[0])
    
    # Segment text between consecutive headings
    for idx, (line_idx, sec, raw_name) in enumerate(found_headings):
        start = line_idx + 1
        end = found_headings[idx+1][0] if idx + 1 < len(found_headings) else len(lines)
        section_text = "\n".join(lines[start:end]).strip()
        
        # If section is already populated, append (e.g. matching multiple "Projects" or "Education" subsections)
        if sections[sec]:
            sections[sec] += "\n\n" + section_text
        else:
            sections[sec] = section_text
            
    # Clean up and normalize spacing
    for sec in sections:
        sections[sec] = sections[sec].strip()
        
    return sections

def parse_resume(pdf_path):
    """
    Complete parser pipeline. Returns a dictionary of all parsed resume elements.
    """
    raw_text = extract_text_from_pdf(pdf_path)
    
    # Standard cleanups (converting double spaces, correcting strange encodings)
    cleaned_text = re.sub(r'\s+', ' ', raw_text)
    
    name = extract_name(raw_text)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    
    sections = parse_sections(raw_text)
    
    return {
        'parsed_text': raw_text,
        'name': name,
        'email': email,
        'phone': phone,
        'education': sections['education'],
        'experience': sections['experience'],
        'projects': sections['projects'],
        'certifications': sections['certifications'],
        'skills_section': sections['skills']
    }
