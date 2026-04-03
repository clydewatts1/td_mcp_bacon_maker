import sqlite3
import pytest
import shutil
import os
import copy
from bacon_maker.engine import execute_job
from bacon_maker.security import enforce_domain_role, SecurityViolationError
from bacon_maker.artifacts import BASE_TMP_DIR

@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()

def test_security_sandbox_advanced():
    """Verify complex DOMAIN_ROLE wildcard patterns."""
    roles = ["PROD_SALES.%", "FINANCE.PAYROLL_%", "GLOBAL.%"]
    
    # Authorized
    assert enforce_domain_role("PROD_SALES.ORDERS", roles) is True
    assert enforce_domain_role("FINANCE.PAYROLL_2024", roles) is True
    assert enforce_domain_role("GLOBAL.USERS", roles) is True
    
    # Violations
    with pytest.raises(SecurityViolationError):
        enforce_domain_role("FINANCE.REPORTS", roles)
    with pytest.raises(SecurityViolationError):
        enforce_domain_role("INTERNAL_DB.LOGS", roles)

def test_chaos_monkey_total_failure(db):
    """Verify that 1.0 probability halts every step."""
    job_config = {
        "job_id": "chaos_total",
        "job_name": "Chaos Total",
        "parameters": {},
        "chaos_monkey": {"enabled": True, "probability": 1.0, "error_codes": [{"error_code": 66, "description": "AGENT_CHAOS"}]},
        "steps": [{"step_id": "s1", "step_type": "SIMPLE", "transaction_enabled": False, "sql_templates": [{"name": "t1", "template_ref": "SELECT 1;", "lint_enabled": False}]}]
    }
    
    trace = execute_job(job_config, db)
    assert trace["status"] == "FAILED"
    assert trace["steps"]["s1"]["templates"][0]["status"] == "CHAOS_FAILURE"

def test_job_recovery_logic(db):
    """Verify that mode='restart' skips successful steps and uses run_on_restart logic."""
    # step_01 will succeed, step_02 will fail in run 1, then succeed in run 2.
    db.execute("CREATE TABLE recovery (step_id TEXT);")
    db.commit()
    
    job_config = {
        "job_id": "recovery_test",
        "job_name": "Recovery Test",
        "parameters": {},
        "global_sql_validation": False,
        "steps": [
            {
                "step_id": "step_01",
                "step_type": "SIMPLE",
                "transaction_enabled": True,
                "run_condition": "true",
                "run_on_restart": "false", # Should skip on restart
                "sql_templates": [{"name": "i1", "template_ref": "INSERT INTO recovery VALUES ('S1');", "lint_enabled": False}]
            },
            {
                "step_id": "step_02",
                "step_type": "SIMPLE",
                "transaction_enabled": True,
                "run_condition": "true",
                "run_on_restart": "true", # Should run on restart
                "sql_templates": [{"name": "i2", "template_ref": "INSERT INTO recovery VALUES ('S2');", "lint_enabled": False}]
            }
        ]
    }
    
    # RUN 1: Inject failure manually in step 2 (mangled SQL)
    fail_config = copy.deepcopy(job_config)
    fail_config["steps"][1]["sql_templates"][0]["template_ref"] = "INSERT INTOO fail;"
    trace1 = execute_job(fail_config, db)
    assert trace1["status"] == "FAILED"
    assert trace1["steps"]["step_01"]["status"] == "SUCCESS"
    
    # Verify S1 inserted
    res1 = db.execute("SELECT count(*) FROM recovery WHERE step_id='S1'").fetchone()
    assert res1[0] == 1
    
    # RUN 2: RESTART with correct config
    trace2 = execute_job(job_config, db, mode='restart')
    assert trace2["status"] == "SUCCESS"
    
    # Verify S1 was NOT inserted again (skipped) and S2 was inserted
    res1_check = db.execute("SELECT count(*) FROM recovery WHERE step_id='S1'").fetchone()
    assert res1_check[0] == 1 # Still 1
    
    res2_check = db.execute("SELECT count(*) FROM recovery WHERE step_id='S2'").fetchone()
    assert res2_check[0] == 1 # Now 1

def teardown_module(module):
    if os.path.exists(BASE_TMP_DIR):
        shutil.rmtree(BASE_TMP_DIR)
