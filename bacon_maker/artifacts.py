import os
import shutil

BASE_TMP_DIR = "job_tmp"

def setup_job_directory(job_name: str) -> str:
    """
    Wipes the job_tmp/<job_name> directory if it exists and recreates a fresh one.
    As defined in the Constitution Section IX.
    """
    job_path = os.path.join(BASE_TMP_DIR, job_name)
    
    if os.path.exists(job_path):
        shutil.rmtree(job_path)
        
    os.makedirs(job_path, exist_ok=True)
    return job_path

def write_artifact(job_name: str, file_name: str, content: str) -> str:
    """Saves a rendered artifact to the job's temporary directory."""
    job_path = os.path.join(BASE_TMP_DIR, job_name)
    
    # Ensure directory exists (defensive check)
    if not os.path.exists(job_path):
        os.makedirs(job_path, exist_ok=True)
        
    file_path = os.path.join(job_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    return file_path
