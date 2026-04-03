from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field

class DomainRole(BaseModel):
    """Defines the database, schema, and table wildcards for a user's sandbox."""
    database: str
    schema_name: str = Field(alias="schema") # Using alias because 'schema' is a common keyword
    table: str

    class Config:
        populate_by_name = True

class UserProfile(BaseModel):
    """The secure YAML profile defining an agent's permissions and sandbox."""
    user_id: str
    name: str
    domain_role: List[DomainRole]
    action_role: List[str]

class ChaosMonkey(BaseModel):
    """Configuration for simulating non-deterministic failures."""
    enabled: bool
    probability: float
    error_codes: List[Dict[str, int]]

class SqlTemplate(BaseModel):
    """Metadata for a single Jinja SQL template and its execution rules."""
    name: str
    template_ref: str
    lint_enabled: bool
    timeout_seconds: Optional[int] = None
    max_rows: Optional[int] = None
    validation_condition: Optional[str] = None
    restart_condition: Optional[str] = None

class Step(BaseModel):
    """A single execution step in a Job, which can be SIMPLE or a LOOP."""
    step_id: str
    step_type: Literal['SIMPLE', 'LOOP']
    run_condition: Optional[str] = None
    run_on_restart: Optional[str] = None
    transaction_enabled: bool
    loop_on: Optional[str] = None
    sql_templates: List[SqlTemplate]

class JobMetadata(BaseModel):
    """The top-level configuration for a Bacon Maker orchestration job."""
    job_id: str
    job_name: str
    global_sql_validation: bool
    chaos_monkey: Optional[ChaosMonkey] = None
    parameters: Dict
    steps: List[Step]
