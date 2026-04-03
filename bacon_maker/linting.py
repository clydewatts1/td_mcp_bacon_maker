import sqlfluff
from typing import Dict, Any

def validate_sql(sql_content: str, dialect: str = 'ansi') -> Dict[str, Any]:
    """
    Lints the provided SQL string using the sqlfluff Python API.
    As defined in the Constitution Section IV.
    """
    try:
        # sqlfluff.lint returns a list of violations
        violations = sqlfluff.lint(sql_content, dialect=dialect)
        
        is_valid = len(violations) == 0
        errors = [v for v in violations]
        
        return {
            "is_valid": is_valid,
            "errors": errors
        }
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [{"message": str(e), "line_no": 0, "line_pos": 0}]
        }
