import pytest
import os


@pytest.fixture(scope="session")
def uvvm_path():
    return os.path.abspath("../../../UVVM")


@pytest.fixture(scope="session")
def tb_path():
    return os.path.abspath("../tb")


@pytest.fixture(scope="session")
def dut_path():
    return os.path.abspath("../dut")


@pytest.fixture(scope="session")
def precompiled_path():
    return os.path.abspath("../precompiled")


@pytest.fixture(scope="session")
def design_path():
    return os.path.abspath("../design")
