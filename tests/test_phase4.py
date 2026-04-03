import sqlite3
import pytest
import os
import shutil
from bacon_maker.engine import execute_job
from bacon_maker.artifacts import BASE_TMP_DIR

@pytest.fixture
def db_conn():
    """In-memory SQLite database for testing."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_e2e_success(db_conn):
    """Verify a successful multi-step job run."""
    job_config = {
        "job_id": "e2e_success_test",
        "job_name": "E2E Success",
        "global_sql_validation": True,
        "parameters": {},
        "steps": [
            {
                "step_id": "step_01_create",
                "step_type": "SIMPLE",
                "transaction_enabled": True,
                "sql_templates": [
                    {"name": "create_table", "template_ref": "CREATE TABLE users (id INT, name TEXT);", "lint_enabled": False}
                ]
            },
            {
                "step_id": "step_02_insert",
                "step_type": "SIMPLE",
                "transaction_enabled": True,
                "sql_templates": [
                    {"name": "insert_row", "template_ref": "INSERT INTO users VALUES (1, 'Alice');", "lint_enabled": False}
                ]
            }
        ]
    }
    
    trace = execute_job(job_config, db_conn)
    assert trace["status"] == "SUCCESS"
    assert trace["steps"]["step_02_insert"]["status"] == "SUCCESS"
    
    # Verify DB state
    res = db_conn.execute("SELECT name FROM users").fetchone()
    assert res[0] == "Alice"

def test_transaction_rollback(db_conn):
    """Verify that a failure in a transaction_enabled step rolls back the DB."""
    # Setup table first
    db_conn.execute("CREATE TABLE users (id INT, name TEXT);")
    db_conn.commit()
    
    job_config = {
        "job_id": "rollback_test",
        "job_name": "Rollback Test",
        "global_sql_validation": True,
        "parameters": {},
        "steps": [
            {
                "step_id": "step_01_failing_transaction",
                "step_type": "SIMPLE",
                "transaction_enabled": True,
                "sql_templates": [
                    {"name": "insert_valid", "template_ref": "INSERT INTO users VALUES (2, 'Bob');", "lint_enabled": False},
                    {"name": "insert_invalid", "template_ref": "INSERT INTOO users VALUES (3, 'Charlie');", "lint_enabled": False}
                ]
            }
        ]
    }
    
    trace = execute_job(job_config, db_conn)
    assert trace["status"] == "FAILED"
    
    # Verify DB is empty because of rollback
    res = db_conn.execute("SELECT count(*) FROM users").fetchone()
    assert res[0] == 0

def test_chaos_monkey_trigger(db_conn):
    """Verify that Chaos Monkey correctly halts execution and reports failure."""
    job_config = {
        "job_id": "chaos_test",
        "job_name": "Chaos Test",
        "global_sql_validation": True,
        "chaos_monkey": {
            "enabled": True,
            "probability": 1.0,
            "error_codes": [{"error_code": -1, "description": "AGENT_CHAOS"}]
        },
        "parameters": {},
        "steps": [
            {
                "step_id": "step_01",
                "step_type": "SIMPLE",
                "transaction_enabled": False,
                "sql_templates": [
                    {"name": "simple_sql", "template_ref": "SELECT 1;", "lint_enabled": False}
                ]
            }
        ]
    }
    
    trace = execute_job(job_config, db_conn)
    assert trace["status"] == "FAILED"
    assert trace["steps"]["step_01"]["templates"][0]["status"] == "CHAOS_FAILURE"
    assert trace["steps"]["step_01"]["templates"][0]["error"] == "AGENT_CHAOS"

def teardown_module(module):
    """Clean up artifacts after tests."""
    if os.path.exists(BASE_TMP_DIR):
        shutil.rmtree(BASE_TMP_DIR)
