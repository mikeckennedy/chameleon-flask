from pathlib import Path

import chameleon_flask as fc
import pytest


@pytest.fixture
def test_templates_path(pytestconfig):
    return Path(pytestconfig.rootdir, 'tests', 'templates')


@pytest.fixture
def setup_global_template(test_templates_path):
    fc.global_init(str(test_templates_path))
    yield
    # Clear paths to no effect future tests
    fc.engine.clear()
