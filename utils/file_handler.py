"""
utils/file_handler.py – File Upload Validation & Storage
==========================================================
This module handles everything related to file uploads:
1. Validates that the uploaded file is a PDF or DOCX
2. Generates a secure filename to prevent security issues
3. Saves the file to the uploads/ folder

KEY CONCEPTS FOR BEGINNERS:
──────────────────────────
- werkzeug.utils.secure_filename: Converts a filename to a safe version.
  Example: "../../evil.pdf" → "evil.pdf" (prevents directory traversal attacks)
  
- uuid: Generates a unique ID to prevent filename collisions.
  If two users upload "resume.pdf", they won't overwrite each other.
  
- File extension check: We check the extension to ensure only allowed file types
  are uploaded. This is a basic security measure.
"""

import os
import uuid
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, MIN_CONTENT_LENGTH, MAX_CONTENT_LENGTH


def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    How it works:
    1. '.' in filename → ensures the file has an extension
    2. filename.rsplit('.', 1)[1] → splits from the right and takes the extension
       Example: "resume.pdf" → splits into ["resume", "pdf"] → takes "pdf"
    3. .lower() → converts to lowercase for case-insensitive comparison
    4. Checks if the extension is in ALLOWED_EXTENSIONS {'pdf', 'docx'}
    
    Parameters:
        filename (str): The original filename from the upload
    
    Returns:
        bool: True if file type is allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """
    Validate and save an uploaded file securely.
    
    Steps:
    1. Check if a file was actually selected
    2. Validate the file extension
    3. Generate a unique filename using UUID
    4. Save to the uploads/ folder
    
    Parameters:
        file: Flask's FileStorage object from request.files
    
    Returns:
        tuple: (success: bool, result: str)
            - On success: (True, filepath)
            - On failure: (False, error_message)
    """
    # Step 1: Check if a file was provided
    if file is None or file.filename == '':
        return False, "No file selected. Please choose a PDF or DOCX file."
    
    # Step 2: Validate file extension
    if not allowed_file(file.filename):
        return False, "Invalid file type. Only PDF and DOCX files are accepted."
    
    # Step 3: Generate a secure, unique filename
    # secure_filename() removes any dangerous characters from the filename
    original_filename = secure_filename(file.filename)
    
    # Extract the file extension
    file_extension = original_filename.rsplit('.', 1)[1].lower()
    
    # Create a unique filename using UUID to prevent collisions
    # Example: "a1b2c3d4-resume.pdf"
    unique_filename = f"{uuid.uuid4().hex[:8]}_{original_filename}"
    
    # Step 4: Ensure the upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Step 5: Build the full file path and save
    filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
    
    try:
        file.save(filepath)

        # Validate minimum file size (50 KB)
        file_size = os.path.getsize(filepath)
        if file_size < MIN_CONTENT_LENGTH:
            os.remove(filepath)  # Clean up the too-small file
            min_kb = MIN_CONTENT_LENGTH // 1024
            actual_kb = round(file_size / 1024, 1)
            return False, (
                f"File is too small ({actual_kb} KB). "
                f"Please upload a resume that is at least {min_kb} KB. "
                "Very small files are usually incomplete or corrupted."
            )

        # Validate magic bytes (file signature) to prevent disguised uploads
        # e.g. someone renaming 'malware.exe' as 'resume.pdf' to bypass extension check
        with open(filepath, 'rb') as f:
            header = f.read(8)

        valid_magic = False
        if file_extension == 'pdf' and header[:4] == b'%PDF':
            valid_magic = True
        elif file_extension == 'docx' and header[:2] == b'PK':  # DOCX is a ZIP archive
            valid_magic = True

        if not valid_magic:
            os.remove(filepath)
            return False, (
                f"The uploaded file does not appear to be a valid {file_extension.upper()}. "
                "Please ensure you are uploading a genuine PDF or DOCX resume file."
            )

        return True, filepath
    except Exception as e:
        return False, f"Failed to save file: {str(e)}"


def get_file_extension(filepath):
    """
    Get the file extension from a filepath.
    
    Parameters:
        filepath (str): Path to the file
    
    Returns:
        str: The extension in lowercase (e.g., 'pdf', 'docx')
    """
    return filepath.rsplit('.', 1)[1].lower() if '.' in filepath else ''


def delete_file(filepath):
    """
    Delete a file from disk (used for cleanup).
    
    Parameters:
        filepath (str): Path to the file to delete
    
    Returns:
        bool: True if deleted successfully, False otherwise
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False
    except Exception:
        return False
