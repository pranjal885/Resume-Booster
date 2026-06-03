import os
from werkzeug.utils import secure_filename

def allowed_file(filename, allowed_extensions):
    """
    Checks if the filename has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

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
        # Avoid duplicate names by checking if path exists, appending numeric suffixes if needed
        base, extension = os.path.splitext(filename)
        counter = 1
        unique_filename = filename
        
        while os.path.exists(os.path.join(upload_folder, unique_filename)):
            unique_filename = f"{base}_{counter}{extension}"
            counter += 1
            
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename, file_path
    except Exception as e:
        return None, f"Failed to save file: {str(e)}"
