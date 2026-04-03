import fnmatch
from typing import List

class SecurityViolationError(Exception):
    """Custom exception raised when a security sandbox rule is breached."""
    pass

def enforce_domain_role(target_object: str, domain_roles: List[str]) -> bool:
    """
    Evaluates a target_object (e.g., 'DATABASE.TABLE') against allowed patterns.
    Supports SQL-style '%' as a wildcard by translating it to glob-style '*'.
    
    Raises SecurityViolationError if no match is found.
    """
    # Normalize the target for comparison
    target = target_object.upper()
    
    # Translate SQL wildcards (%) to glob wildcards (*) and ensure upper case
    patterns = [p.replace('%', '*').upper() for p in domain_roles]
    
    for pattern in patterns:
        if fnmatch.fnmatch(target, pattern):
            return True
            
    # If no pattern matches, the access is unauthorized
    raise SecurityViolationError(
        f"SECURITY_VIOLATION_ERROR: Target '{target_object}' is outside the authorized DOMAIN_ROLE."
    )
