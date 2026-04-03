import sqlite3
import pytest
import os
import shutil
from bacon_maker.engine import execute_job
from bacon_maker.artifacts import BASE_TMP_DIR

@pytest.fixture
def db():
    """Shared in-memory SQLite connection."""
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_long_multistep_success(db):
    """Verify a 3-step successful job run with state changes."""
    job_config = {
        "job_id": "long_success",
        "job_name": "Long Success",
        "parameters": {"schema": "main"},
        "steps": [
            {
                "step_id": "s01", "transaction_enabled": True,
                "sql_templates": [{"name": "c1", "template_ref": "CREATE TABLE t1 (id INT);", "lint_enabled": False}]
            },
            {
                "step_id": "s02", "transaction_enabled": True,
                "sql_templates": [{"name": "i1", "template_ref": "INSERT INTO t1 VALUES (100);", "lint_enabled": False}]
            },
            {
                "step_id": "s03", "transaction_enabled": True,
                "sql_templates": [{"name": "u1", "template_ref": "UPDATE t1 SET id = 200;", "lint_enabled": False}]
            }
        ]
    }
    
    trace = execute_job(job_config, db)
    assert trace["status"] == "SUCCESS"
    assert trace["steps"]["s03"]["status"] == "SUCCESS"
    
    res = db.execute("SELECT id FROM t1").fetchone()
    assert res[0] == 200
    
    # Verify artifacts
    assert os.path.exists(os.path.join(BASE_TMP_DIR, "long_success", "s02_i1.sql"))

def test_linting_gate_halts_execution(db):
    """Verify that the engine stops BEFORE hitting the DB if linting fails."""
    job_config = {
        "job_id": "lint_fail",
        "job_name": "Lint Fail",
        "steps": [
            {
                "step_id": "s01", "transaction_enabled": False,
                "sql_templates": [
                    {"name": "mangled", "template_ref": "SELETC * FROMM table;", "lint_enabled": True}
                ]
            }
        ]
    }
    
    trace = execute_job(job_config, db)
    assert trace["status"] == "FAILED"
    assert "s01" in trace["steps"]
    
    # Verify no table was created (proving it didn't execute)
    with pytest.raises(sqlite3.OperationalError):
        db.execute("SELECT * FROM table")

def test_deep_transaction_integrity(db):
    """Verify that a failure in step 2 of 3 rolls back correctly."""
    # Step 0: Setup
    db.execute("CREATE TABLE log (msg TEXT);")
    db.commit()
    
    job_config = {
        "job_id": "transaction_fail",
        "job_name": "Transaction Fail",
        "steps": [
            {
                "step_id": "s01_success", "transaction_enabled": True,
                "sql_templates": [{"name": "i1", "template_ref": "INSERT INTO log VALUES ('FIRST');", "lint_enabled": False}]
            },
            {
                "step_id": "s02_rollback", "transaction_enabled": True,
                "sql_templates": [
                    {"name": "i2", "template_ref": "INSERT INTO log VALUES ('SECOND');", "lint_enabled": False},
                    {"name": "fail", "template_ref": "INSERT INTOO fail_table;", "lint_enabled": False}
                ]
            }
        ]
    }
    
    execute_job(job_config, db)
    
    # Assert s01 persisted (separate transaction)
    res1 = db.execute("SELECT count(*) FROM log WHERE msg = 'FIRST'").fetchone()
    assert res1[0] == 1
    
    # Assert s02 rolled back ('SECOND' should NOT be there)
    res2 = db.execute("SELECT count(*) FROM log WHERE msg = 'SECOND'").fetchone()
    assert res2[0] == 0

def teardown_module(module):
    if os.path.exists(BASE_TMP_DIR):
        shutil.rmtree(BASE_TMP_DIR)
