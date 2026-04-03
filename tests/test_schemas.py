import pytest
from pydantic import ValidationError
from bacon_maker.schemas import UserProfile, JobMetadata

def test_valid_user_profile():
    mock_data = {
        "user_id": "agent_alpha_01",
        "name": "Bacon Maker Prod Agent",
        "domain_role": [
            {"database": "PROD_SALES%", "schema": "%", "table": "%"}
        ],
        "action_role": ["DISCOVER", "DEVELOP", "EXECUTE", "RECOVER"]
    }
    profile = UserProfile(**mock_data)
    assert profile.user_id == "agent_alpha_01"
    assert profile.domain_role[0].schema_name == "%"

def test_valid_job_metadata():
    mock_data = {
        "job_id": "sales_load_2024",
        "job_name": "Sales Data Load",
        "global_sql_validation": True,
        "parameters": {"batch_id": 123},
        "steps": [
            {
                "step_id": "step_01",
                "step_type": "SIMPLE",
                "transaction_enabled": True,
                "sql_templates": [
                    {
                        "name": "fact_insert",
                        "template_ref": "fact_load.jinja",
                        "lint_enabled": True
                    }
                ]
            }
        ]
    }
    job = JobMetadata(**mock_data)
    assert job.job_id == "sales_load_2024"
    assert len(job.steps) == 1

def test_invalid_job_id_missing():
    mock_data = {
        "job_name": "Broken Job",
        "global_sql_validation": True,
        "parameters": {},
        "steps": []
    }
    with pytest.raises(ValidationError):
        JobMetadata(**mock_data)

def test_invalid_step_type():
    mock_data = {
        "job_id": "broken_step",
        "job_name": "Broken Step Type",
        "global_sql_validation": True,
        "parameters": {},
        "steps": [
            {
                "step_id": "step_01",
                "step_type": "COMPLEX",  # Invalid type according to Literal
                "transaction_enabled": True,
                "sql_templates": []
            }
        ]
    }
    with pytest.raises(ValidationError):
        JobMetadata(**mock_data)
