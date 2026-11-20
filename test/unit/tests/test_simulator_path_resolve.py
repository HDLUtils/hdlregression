#
# Tests for locating the correct simulator executables when several simulators that share
# executable names (vsim, vcom, vlog, vlib, vmap) are installed and in PATH,
# e.g. ModelSim/Questa and Riviera-PRO. No simulator installation is required.
#
import os
import sys
import stat
from unittest import mock

import pytest

from hdlregression import settings as hdl_settings
from hdlregression.settings import (
    find_exec_dir,
    ModelsimSettings,
    RivieraProSettings,
    ActiveHDLSettings,
    GHDLSettings,
)


def _make_exec(directory, name):
    filename = name + ".exe" if sys.platform.startswith("win") else name
    path = os.path.join(str(directory), filename)
    with open(path, "w") as f:
        f.write("")
    os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return path


@pytest.fixture
def two_simulators(tmp_path, monkeypatch):
    """Riviera-PRO first in PATH, ModelSim/Questa second; both provide 'vsim'."""
    riviera_bin = tmp_path / "riviera" / "bin"
    questa_bin = tmp_path / "questa" / "bin"
    riviera_bin.mkdir(parents=True)
    questa_bin.mkdir(parents=True)
    for exe in ("vsim", "vcom", "vlog", "vlib", "vmap", "vsimsa"):
        _make_exec(riviera_bin, exe)
    for exe in ("vsim", "vcom", "vlog", "vlib", "vmap"):
        _make_exec(questa_bin, exe)

    def fake_version(executable, version_call="-version"):
        if os.path.normcase(str(riviera_bin)) in os.path.normcase(executable):
            return "Aldec, Inc. Riviera-PRO version 2023.04"
        if os.path.normcase(str(questa_bin)) in os.path.normcase(executable):
            return "Questa Sim-64 vsim 2023.1 Simulator 2023.01 Jan 23 2023"
        return ""

    monkeypatch.setenv("PATH", os.pathsep.join([str(riviera_bin), str(questa_bin)]))
    monkeypatch.setattr(hdl_settings, "_exec_version_output", fake_version)
    return riviera_bin, questa_bin


def _same_dir(a, b):
    return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))


def test_find_exec_dir_filters_on_version_output(two_simulators):
    riviera_bin, questa_bin = two_simulators
    assert _same_dir(find_exec_dir("vsim", ids=("modelsim", "questa")), questa_bin)
    assert _same_dir(find_exec_dir("vsimsa"), riviera_bin)
    assert find_exec_dir("vsim", ids=("active-hdl",)) is None


def test_modelsim_uses_modelsim_dir_even_if_riviera_first_in_path(two_simulators):
    _, questa_bin = two_simulators
    exe = ModelsimSettings().get_simulator_exec("vsim")
    assert _same_dir(os.path.dirname(exe), questa_bin)


def test_riviera_uses_riviera_dir_even_if_modelsim_first_in_path(two_simulators, monkeypatch):
    riviera_bin, questa_bin = two_simulators
    monkeypatch.setenv("PATH", os.pathsep.join([str(questa_bin), str(riviera_bin)]))
    for exe_name in ("vsim", "vcom", "vlog", "vlib", "vmap"):
        exe = RivieraProSettings().get_simulator_exec(exe_name)
        assert _same_dir(os.path.dirname(exe), riviera_bin)
        assert os.path.basename(exe) == exe_name


def test_explicit_simulator_path_wins(two_simulators, tmp_path):
    custom = tmp_path / "custom"
    custom.mkdir()
    s = RivieraProSettings()
    s.set_simulator_path(str(custom))
    assert s.get_simulator_exec("vsim") == os.path.join(str(custom), "vsim")
    assert s.get_simulator_path() == str(custom)


def test_auto_path_not_reported_as_user_path(two_simulators):
    s = RivieraProSettings()
    s.get_simulator_exec("vsim")
    assert s.get_simulator_path() is None


def test_fallback_to_bare_name_when_not_found(two_simulators):
    # Active-HDL is not in the fake PATH
    assert ActiveHDLSettings().get_simulator_exec("vsim") == "vsim"


def test_unique_exec_simulators_unchanged(two_simulators):
    assert GHDLSettings().get_simulator_exec("ghdl") == "ghdl"


def test_cli_selected_simulator_ignores_script_path(tmp_path):
    """-s riviera on the CLI + set_simulator('modelsim', path=...) in the script must not
    apply the ModelSim path to Riviera-PRO."""
    from hdlregression.hdlregression import HDLRegression
    from hdlregression.settings import SimulatorDetector

    hr = HDLRegression.__new__(HDLRegression)
    hr.logger = mock.Mock()
    hr.settings = mock.Mock()
    hr.settings.simulator_detector = SimulatorDetector.__new__(SimulatorDetector)
    hr.settings.get_simulator_name.return_value = "RIVIERA-PRO"

    hr.set_simulator("modelsim", path=str(tmp_path), com_options="-foo")

    hr.settings.set_simulator_path.assert_not_called()
    hr.settings.set_com_options.assert_not_called()


def test_script_path_applied_when_simulator_matches(tmp_path):
    from hdlregression.hdlregression import HDLRegression
    from hdlregression.settings import SimulatorDetector

    hr = HDLRegression.__new__(HDLRegression)
    hr.logger = mock.Mock()
    hr.settings = mock.Mock()
    hr.settings.simulator_detector = SimulatorDetector.__new__(SimulatorDetector)
    hr.settings.get_simulator_name.return_value = "RIVIERA-PRO"

    hr.set_simulator("riviera", path=str(tmp_path))

    hr.settings.set_simulator_path.assert_called_once_with(str(tmp_path))
