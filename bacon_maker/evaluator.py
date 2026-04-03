import celpy
from typing import Any, Dict, Optional

def evaluate_condition(expression: Optional[str], context: Dict[str, Any]) -> bool:
    """
    Setup a secure evaluator using celpy to evaluate CEL expressions.
    Returns True if the expression is empty or None.
    """
    if not expression or expression.strip() == "":
        return True
    
    try:
        # Initialize the CEL environment
        env = celpy.Environment()
        
        # Compile the expression into an AST
        ast = env.compile(expression)
        
        # Create an executable program from the AST
        prgm = env.program(ast)
        
        # Map the Python dictionary to a CEL-compatible object
        cel_context = celpy.json_to_cel(context)
        
        # Evaluate directly using the CEL context
        result = prgm.evaluate(cel_context)
        return bool(result)
        
    except Exception as e:
        # Catching generic Exception for robustness in this phase
        raise ValueError(f"CEL Evaluation Error: {str(e)} in expression '{expression}'")
