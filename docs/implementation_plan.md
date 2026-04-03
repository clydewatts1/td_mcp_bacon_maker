# Implementation Plan - Phase 0: Environment Setup (The Foundation)

This plan covers the initialization of the Antigravity project environment, focusing on reproducibility, security, and dependency management.

## User Review Required

> [!IMPORTANT]
> The current workspace is `td_mcp_bacon_maker`. The instructions mention creating a folder named `antigravity`. I will create an `antigravity` subdirectory for the source code, but keep the root configuration files (requirements, gitignore, etc.) in the project root unless otherwise specified.

## Proposed Changes

### Environment Initialization
- Initialize a Python virtual environment (`venv`) in the root directory.
- Ensure Git is tracking the project (already initialized in the current workspace).

### Configuration Files
#### [MODIFY] [README.md](file:///c:/Users/cw171001/Projects/td_mcp_bacon_maker/README.md)
- Update the README with a project description for Antigravity.

#### [NEW] [requirements.txt](file:///c:/Users/cw171001/Projects/td_mcp_bacon_maker/requirements.txt)
- List all required dependencies as specified: `mcp`, `pydantic`, `PyYAML`, `python-dotenv`, `Jinja2`, `cel-python`, `sqlfluff`, `teradatasql`, `mysql-connector-python`, `pytest`, `pytest-asyncio`.

#### [NEW] [.gitignore](file:///c:/Users/cw171001/Projects/td_mcp_bacon_maker/.gitignore)
- Configure Git to ignore sensitive and temporary files: `.env`, `venv/`, `__pycache__/`, `*.pyc`, `job_tmp/`.

#### [NEW] [.env.example](file:///c:/Users/cw171001/Projects/td_mcp_bacon_maker/.env.example)
- Provide a template for required environment variables: `TERADATA_PWD`, `MYSQL_PWD`.

### Testing Infrastructure
#### [NEW] [tests/test_env.py](file:///c:/Users/cw171001/Projects/td_mcp_bacon_maker/tests/test_env.py)
- Create a verification script to ensure core dependencies are importable.

## Verification Plan

### Automated Tests
- Run `pytest tests/test_env.py` within the virtual environment to confirm all core libraries (`pydantic`, `mcp`, `jinja2`, `dotenv`) are correctly installed and accessible.

### Manual Verification
- Verify the presence of all generated files in the workspace.
- Confirm `.gitignore` correctly reflects the requirements.
