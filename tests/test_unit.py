import pytest
from pydantic import ValidationError
from bacon_maker.schemas import JobMetadata, UserProfile
from bacon_maker.evaluator import evaluate_condition
from bacon_maker.templating import map_type

# 1. SCHEMA VALIDATION TESTS
def test_user_profile_validation():
    """Exhaustive validation of UserProfile schema."""
    # Valid - Minimal
    valid_data = {
        "user_id": "u01", "name": "Agent",
        "domain_role": [{"database": "DB", "schema": "S", "table": "T"}],
        "action_role": ["READ"]
    }
    assert UserProfile(**valid_data).user_id == "u01"
    
    # Valid - Wildcards
    valid_wildcard = {
        "user_id": "u02", "name": "Agent",
        "domain_role": [{"database": "PROD_%", "schema": "%", "table": "%"}],
        "action_role": ["READ", "WRITE"]
    }
    assert UserProfile(**valid_wildcard).domain_role[0].database == "PROD_%"
    
    # Invalid - Missing required field
    with pytest.raises(ValidationError):
        UserProfile(user_id="fail")
        
    # Invalid - Wrong types
    with pytest.raises(ValidationError):
        UserProfile(user_id="fail", name=123, domain_role="wrong", action_role=[1])

def test_job_metadata_validation():
    """Exhaustive validation of JobMetadata schema."""
    valid_job = {
        "job_id": "j01", "job_name": "Test Job", "global_sql_validation": True,
        "parameters": {"env": "prod"},
        "steps": [
            {
                "step_id": "s01", "step_type": "SIMPLE", "transaction_enabled": True,
                "sql_templates": [{"name": "t1", "template_ref": "SELECT 1;", "lint_enabled": True}]
            }
        ]
    }
    assert JobMetadata(**valid_job).job_id == "j01"
    
    # Invalid - Missing step_id
    invalid_job = valid_job.copy()
    invalid_job["steps"][0].pop("step_id")
    with pytest.raises(ValidationError):
        JobMetadata(**invalid_job)

# 2. CEL LOGIC TESTS
@pytest.mark.parametrize("expression,context,expected", [
    ("parameters.env == 'prod'", {"parameters": {"env": "prod"}}, True),
    ("trace.status == 'FAILED'", {"trace": {"status": "FAILED"}}, True),
    ("results.count > 10", {"results": {"count": 12}}, True),
    ("results.count > 10", {"results": {"count": 5}}, False),
    ("parameters.nested.val == 1", {"parameters": {"nested": {"val": 1}}}, True),
    (None, {}, True), # Empty condition defaults to True
    ("", {}, True),
])
def test_cel_evaluation(expression, context, expected):
    """Verify CEL logic across multiple context scenarios."""
    assert evaluate_condition(expression, context) == expected

# 3. DIALECT RENDERING TESTS
@pytest.mark.parametrize("dialect,raw_type,expected", [
    ('teradata', 'I', 'INTEGER'),
    ('teradata', 'I1', 'INTEGER'),
    ('teradata', 'DA', 'DATE'),
    ('teradata', 'CV', 'STRING'),
    ('mysql', 'int', 'INTEGER'),
    ('mysql', 'bigint', 'INTEGER'),
    ('mysql', 'varchar', 'STRING'),
    ('mysql', 'text', 'STRING'),
    ('unknown', 'MY_TYPE', 'MY_TYPE'), # Fallback
])
def test_dialect_mapping(dialect, raw_type, expected):
    """Verify that type mapping normalization is exhaustive."""
    assert map_type(dialect, raw_type) == expected
