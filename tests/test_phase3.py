import pytest
from bacon_maker.evaluator import evaluate_condition
from bacon_maker.security import enforce_domain_role, SecurityViolationError

def test_cel_evaluation_success():
    """Verify that valid CEL expressions correctly identify True conditions."""
    context = {"results": {"error_code": 0}}
    expression = "results.error_code == 0"
    assert evaluate_condition(expression, context) is True

def test_cel_evaluation_failure():
    """Verify that CEL expressions correctly identify False conditions."""
    context = {"results": {"error_code": -1}}
    expression = "results.error_code == 0"
    assert evaluate_condition(expression, context) is False

def test_cel_evaluation_null():
    """Verify that empty expressions default to True."""
    assert evaluate_condition("", {}) is True
    assert evaluate_condition(None, {}) is True

def test_security_sandbox_authorized():
    """Verify that authorized targets pass the security gate."""
    domain_roles = ["PROD_SALES%", "FINANCE.REPORTS"]
    
    # Match via wildcard
    assert enforce_domain_role("PROD_SALES.ORDERS", domain_roles) is True
    # Match via exact string
    assert enforce_domain_role("FINANCE.REPORTS", domain_roles) is True

def test_security_sandbox_violation():
    """Verify that unauthorized targets raise a SecurityViolationError."""
    domain_roles = ["PROD_SALES%"]
    
    with pytest.raises(SecurityViolationError) as excinfo:
        enforce_domain_role("FINANCE.PAYROLL", domain_roles)
    
    assert "SECURITY_VIOLATION_ERROR" in str(excinfo.value)
