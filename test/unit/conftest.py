import pytest
import os


def is_running_in_docker():
    path_to_check = "/.dockerenv"
    return os.path.exists(path_to_check)


@pytest.fixture(scope="session")
def uvvm_path():
    if is_running_in_docker():
        docker_path = "../../../uvvm"
        return os.path.abspath(docker_path)
    else:
        return os.path.abspath("../../../UVVM/GITHUB_UVVM")


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
