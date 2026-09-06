import re #Python's regular expression module.
import pdfplumber #Used to extract text from PDF files.
import PyPDF2 #Another PDF-reading library.
#In your project, it is used as a fallback if pdfplumber fails.


def extract_text_from_pdf(pdf_path):
    """
    Extracts text from PDF using pdfplumber,
    falling back to PyPDF2 if needed.
    """
    text = ""
    #We're going to keep adding extracted page text into this string.

    try:
        with pdfplumber.open(pdf_path) as pdf:
        #The with statement automatically handles closing the PDF after we're finished.
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                #If text was successfully extracted, add it to our text variable.

    except Exception as e:
        print(f"[PARSER WARNING] pdfplumber failed: {e}")

    # Fallback
    if not text.strip():
        try:
            with open(pdf_path, 'rb') as f:
            #Open the PDF in: rb = read binary mode. PDFs are binary files, so we open them using rb.
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
    #This is a regular expression pattern.

    match = re.search(pattern, text)
    #Searches the entire resume text for the first matching email.

    return match.group(0) if match else None
    #If a match exists → return the email.
    #If there isn't one → return:None

def extract_phone(text):
    """
    Extract phone number using regex.
    """
    pattern = r'(?:(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}?\)?[-.\s]?\d{3,4}[-.\s]?\d{4})'

    matches = re.findall(pattern, text)#findall() finds all matching occurrences.

    for match in matches:
        digits = re.sub(r'\D', '', match)
        #This removes everything that is not a digit.

        if 8 <= len(digits) <= 15:
            return match.strip()

    return None


def extract_name(text):
    """
    Extract probable candidate name from top resume lines.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    #Split resume into lines

    for line in lines[:5]:
        #Only look at first 5 lines
        #Why? Because a resume usually puts the candidate's name near the top.
        #So instead of checking the entire resume, the code checks only the first five meaningful lines.

        # Skip contact info
        if '@' in line: #If the line contains @, it is probably an email.
            continue

        if any(word in line.lower() for word in [
            'resume', 'curriculum', 'cv',
            'email', 'phone', 'portfolio'
        ]):
            continue
        #Skip obvious headings

        words = line.split()#split lines into words

        # Typical name heuristic
        if 2 <= len(words) <= 4: #The code assumes a likely name has between 2 and 4 words.

            if re.match(r'^[a-zA-Z\s\.\-]+$', line):
                return line.title()
            #.title() converts it to title case.
            #For example:
           #pranjal patil
            #becomes:Pranjal Patil

    return "Job Seeker" #If no likely name is found:


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

        start = line_idx + 1 #Start after the heading.

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

