import random
from typing import Optional, Dict, Any

def evaluate_chaos(chaos_config: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Evaluates Whether to trigger a simulated failure based on probability.
    As defined in the Constitution Section III.
    """
    if not chaos_config or not chaos_config.get("enabled"):
        return None
        
    probability = chaos_config.get("probability", 0.0)
    if random.random() < probability:
        error_codes = chaos_config.get("error_codes", [])
        if error_codes:
            # Pick a random simulated error
            error = random.choice(error_codes)
            return {
                "error_code": error.get("error_code", -1),
                "description": error.get("description", "CHAOS_FAILURE"),
                "injected_failure": True
            }
        return {"error_code": -1, "description": "UNKNOWN_CHAOS_ERROR", "injected_failure": True}
        
    return None
