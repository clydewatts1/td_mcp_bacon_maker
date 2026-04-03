import pytest
import pydantic
import mcp
import jinja2
import dotenv
import os

def test_imports():
    """Verify that core dependencies are correctly installed and importable."""
    # Using more robust checks for some libraries
    assert pydantic.__version__ is not None
    # mcp might be a package, checking its name or a key attribute
    assert mcp is not None
    assert jinja2.__version__ is not None
    assert dotenv.load_dotenv is not None
    print("Core imports verified.")

if __name__ == "__main__":
    test_imports()
    print("Environment Verification Successful!")
