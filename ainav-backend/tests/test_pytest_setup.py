"""
Test to validate pytest infrastructure setup.

This test ensures that pytest.ini, conftest.py, and coverage configuration
are properly set up and can be imported without errors.
"""
import os
import configparser


def test_pytest_ini_exists():
    """Verify pytest.ini exists and is properly formatted."""
    pytest_ini_path = os.path.join(os.path.dirname(__file__), "..", "pytest.ini")
    assert os.path.exists(pytest_ini_path), "pytest.ini should exist"

    # Try to parse it
    config = configparser.ConfigParser()
    config.read(pytest_ini_path)

    assert "pytest" in config.sections(), "pytest.ini should have [pytest] section"
    assert "testpaths" in config["pytest"], "pytest.ini should define testpaths"


def test_coveragerc_exists():
    """Verify .coveragerc exists and is properly formatted."""
    coveragerc_path = os.path.join(os.path.dirname(__file__), "..", ".coveragerc")
    assert os.path.exists(coveragerc_path), ".coveragerc should exist"

    # Try to parse it
    config = configparser.ConfigParser()
    config.read(coveragerc_path)

    assert "run" in config.sections(), ".coveragerc should have [run] section"
    assert "report" in config.sections(), ".coveragerc should have [report] section"


def test_conftest_exists():
    """Verify conftest.py exists."""
    conftest_path = os.path.join(os.path.dirname(__file__), "..", "conftest.py")
    assert os.path.exists(conftest_path), "conftest.py should exist"


def test_requirements_has_pytest():
    """Verify pytest dependencies are in requirements.txt."""
    requirements_path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
    assert os.path.exists(requirements_path), "requirements.txt should exist"

    with open(requirements_path, "r") as f:
        content = f.read()

    assert "pytest==" in content, "requirements.txt should include pytest"
    assert "pytest-cov==" in content, "requirements.txt should include pytest-cov"
    assert "pytest-asyncio==" in content, "requirements.txt should include pytest-asyncio"
    assert "pytest-mock==" in content, "requirements.txt should include pytest-mock"


def test_testing_documentation_exists():
    """Verify TESTING.md documentation exists."""
    testing_md_path = os.path.join(os.path.dirname(__file__), "..", "TESTING.md")
    assert os.path.exists(testing_md_path), "TESTING.md should exist"

    with open(testing_md_path, "r") as f:
        content = f.read()

    assert "pytest.ini" in content, "TESTING.md should document pytest.ini"
    assert "conftest.py" in content, "TESTING.md should document conftest.py"
