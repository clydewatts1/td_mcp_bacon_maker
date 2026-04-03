import os
import pytest
import shutil
from bacon_maker.templating import render_sql
from bacon_maker.artifacts import setup_job_directory, write_artifact, BASE_TMP_DIR
from bacon_maker.linting import validate_sql

def test_templating_map_type():
    """Verify that the map_type macro resolves correctly in Jinja templates."""
    # Test Teradata CV -> STRING
    tpl = "{{ map_type('teradata', 'CV', length=50) }}"
    res = render_sql(tpl, {})
    assert res == "STRING(50)"
    
    # Test Teradata I -> INTEGER
    tpl = "{{ map_type('teradata', 'I') }}"
    res = render_sql(tpl, {})
    assert res == "INTEGER"
    
    # Test MySQL int -> INTEGER
    tpl = "{{ map_type('mysql', 'int') }}"
    res = render_sql(tpl, {})
    assert res == "INTEGER"

def test_artifacts_lifecycle():
    """Verify directory setup, file writing, and proper wiping."""
    job_name = "test_job_lifecycle"
    
    # 1. Setup fresh directory
    job_dir = setup_job_directory(job_name)
    assert os.path.exists(job_dir)
    
    # 2. Write an artifact
    file_name = "test_artifact.sql"
    content = "SELECT 1;"
    file_path = write_artifact(job_name, file_name, content)
    assert os.path.exists(file_path)
    with open(file_path, "r") as f:
        assert f.read() == content
        
    # 3. Re-setup same job name - must be empty
    setup_job_directory(job_name)
    assert os.path.exists(job_dir)
    assert len(os.listdir(job_dir)) == 0
    
    # Cleanup
    if os.path.exists(BASE_TMP_DIR):
        shutil.rmtree(BASE_TMP_DIR)

def test_linting_validation():
    """Verify sqlfluff validation for valid and invalid SQL."""
    # Valid SQL
    valid_sql = "SELECT column_a FROM my_table;\n"
    res_valid = validate_sql(valid_sql)
    assert res_valid["is_valid"] is True
    
    # Invalid SQL (mangled keyword)
    invalid_sql = "SELECT * FROMM my_table;"
    res_invalid = validate_sql(invalid_sql)
    assert res_invalid["is_valid"] is False
    assert len(res_invalid["errors"]) > 0
