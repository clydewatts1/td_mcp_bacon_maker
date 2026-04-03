import os
from typing import Optional
from jinja2 import Environment, BaseLoader, select_autoescape

def map_type(dialect: str, raw_type: str, length: Optional[int] = None, 
             precision: Optional[int] = None, scale: Optional[int] = None) -> str:
    """
    Normalizes database-specific types to a standard set (INTEGER, STRING, DECIMAL, DATE).
    As defined in the Constitution Section VI.
    """
    d = dialect.lower()
    rt = raw_type.upper()
    
    if d == 'teradata':
        if rt in ['I', 'I1', 'I2', 'I8']:
            return "INTEGER"
        elif rt in ['D', 'F']:
            p = precision if precision is not None else 18
            s = scale if scale is not None else 2
            return f"DECIMAL({p},{s})"
        elif rt in ['CV', 'CF', 'CO']:
            return f"STRING({length})" if length else "STRING"
        elif rt == 'DA':
            return "DATE"
        else:
            return f"UNKNOWN({rt})"
            
    elif d == 'mysql':
        if 'INT' in rt:
            return "INTEGER"
        elif 'CHAR' in rt or 'TEXT' in rt:
            return "STRING"
        else:
            return rt
            
    else:
        return rt

# Configure a secure Jinja2 environment
env = Environment(
    loader=BaseLoader(),
    autoescape=select_autoescape(['html', 'xml']),
    trim_blocks=True,
    lstrip_blocks=True
)

# Register map_type as a global function
env.globals['map_type'] = map_type

def render_sql(template_str: str, context: dict) -> str:
    """Processes a SQL template string with the provided context."""
    template = env.from_string(template_str)
    return template.render(**context)
