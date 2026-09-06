import os
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    """
    Checks if the filename has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions
    #'.' in filename : checks whether file contains .
    #filename.rsplit('.', 1)
    #rsplit() splits from the right side.
    #The 1 means split only once.
    #Example: "my.resume.pdf".rsplit('.', 1)
    #gives: ["my.resume", "pdf"]
    #Then:[1] gets:pdf
    #.lower() converts to lowercase
    # and checks whether that extension is in allowed extensions 

def save_uploaded_file(file, upload_folder, allowed_extensions):
    """
    Validates and saves an uploaded file.
    Returns the secure filename and its absolute path if successful, otherwise None.
    """
    if not file or file.filename == '':
        return None, "No file selected"
        
    if not allowed_file(file.filename, allowed_extensions):
        return None, "Invalid file format. Only PDF files are allowed."
        
    try:
        # Create uploads directory if it does not exist
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
            
        # Secure the filename
        filename = secure_filename(file.filename)
        #Suppose the original filename is:My Resume 2026.pdf
        #secure_filename() converts it into a safer filename such as:My_Resume_2026.pdf

        # Avoid duplicate names by checking if path exists, appending numeric suffixes if needed
        base, extension = os.path.splitext(filename)
        #Separate filename and extension
         #base, extension = os.path.splitext(filename)
         #Suppose: filename = "resume.pdf"
         #Then:
         #base       = "resume"
         #extension  = ".pdf"
        #So we can modify the filename while keeping the extension.
        counter = 1
        unique_filename = filename
        
        while os.path.exists(os.path.join(upload_folder, unique_filename)):
            #Does a file with this name already exist inside the upload folder?
            unique_filename = f"{base}_{counter}{extension}"
            counter += 1
            
        file_path = os.path.join(upload_folder, unique_filename)
        #Create complete path
        file.save(file_path)
        #This actually writes the uploaded file to the specified location.
        
        
        return unique_filename, file_path
    except Exception as e:
        return None, f"Failed to save file: {str(e)}"
