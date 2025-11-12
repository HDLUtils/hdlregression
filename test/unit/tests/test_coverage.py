# ================================================================================================================================
#  Copyright 2021 Bitvis
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 and in the provided LICENSE.TXT.
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and limitations under the License.
# ================================================================================================================================
#  Note : Any functionality not explicitly described in the documentation is subject to change at any time
# --------------------------------------------------------------------------------------------------------------------------------

import pytest
import sys
import os
import platform
import shutil
import subprocess

from pathlib import Path
from types import SimpleNamespace

from hdlregression import HDLRegression
import hdlregression.hdlcodecoverage as hcov


def make_tree_with_ucdb(tmp_path, cov_name="code_coverage.ucdb", n=2):
    """Create a directory tree with dummy UCDB files."""
    base = Path(tmp_path) / "hdlregression" / "test"
    for i in range(n):
        d = base / f"tc_{i}"
        d.mkdir(parents=True, exist_ok=True)
        (d / cov_name).write_text("dummy")
    return base


if len(sys.argv) >= 2:
    # Remove pytest from argument list
    sys.argv.pop(1)


def get_file_path(path) -> str:
    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(TEST_DIR, path)


def clear_output():
    if os.path.isdir("./hdlregression"):
        shutil.rmtree("./hdlregression")


def setup_function():
    if os.path.isdir("./hdlregression"):
        print("WARNING! hdlregression folder already exist!")


def tear_down_function():
    clear_output()


def is_simulator_installed(simulator):
    version = "-version" if simulator == "vsim" else "--version"
    try:
        subprocess.run([simulator, version], check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def is_folder_present(folder_path):
    return os.path.isdir(folder_path)


@pytest.fixture(scope="session")
def sim_env():
    # Detect platform and simulators
    platform_info = platform.system()
    modelsim_installed = is_simulator_installed("vsim")
    ghdl_installed = is_simulator_installed("ghdl")
    nvc_installed = is_simulator_installed("nvc")
    simulator = (
        "MODELSIM"
        if modelsim_installed
        else "NVC"
        if nvc_installed
        else "GHDL"
        if ghdl_installed
        else ""
    )
    return {
        "platform": platform_info,
        "modelsim": modelsim_installed,
        "ghdl": ghdl_installed,
        "nvc": nvc_installed,
        "simulator": simulator,
    }


class FakeLogger:
    def __init__(self):
        self.messages = []
    def info(self, m): self.messages.append(("INFO", m))
    def warning(self, m): self.messages.append(("WARN", m))
    def error(self, m): self.messages.append(("ERR", m))
    def debug(self, m): self.messages.append(("DBG", m))
    def green(self): return ""
    def red(self): return ""
    def reset_color(self): return ""


class FakeSettings:
    def __init__(self, test_path, script_path):
        self._test_path = os.path.abspath(test_path)
        self._script_path = os.path.abspath(script_path)
        self._verbose = False
        self._exec_map = {"vcover": "vcover", "vsim": "vsim"}
    def get_test_path(self): return self._test_path
    def get_script_path(self): return self._script_path
    def get_verbose(self): return self._verbose
    def set_verbose(self, v): self._verbose = bool(v)
    def get_simulator_exec(self, name): return self._exec_map[name]


class FakeProject:
    def __init__(self, test_path, script_path=None):
        if script_path is None:
            script_path = test_path
        self.settings = FakeSettings(test_path, script_path)
        self.logger = FakeLogger()
        self._last_run = SimpleNamespace(cmd=None, verbose=None)
        self.run_log = []
        os.makedirs(self.settings.get_test_path(), exist_ok=True)

    def run_command(self, command, verbose=False):
        # _run_command_str sends in string; save it
        if isinstance(command, list):
            cmd_str = " ".join(command)
        else:
            cmd_str = command
        self.run_log.append(cmd_str)
        self._last_run.cmd = cmd_str
        self._last_run.verbose = verbose
        return ("", 0)


class CaptureCommandRunner:
    """Replace CommandRunner to capture command lists without executing anything."""
    def __init__(self, project=None):
        self.captured = []
    def run(self, command, path="./", env=None, output_file=None):
        self.captured.append(
            {"cmd": command, "path": os.path.abspath(path), "output_file": output_file}
        )
        # yield a line so the code doesn't fail when iterating over the result
        yield ("FAKE: " + " ".join(command), True)

def proj_abs(p):
    return os.path.abspath(str(p))


def test_set_code_coverage(sim_env):
    """Test setting code coverage settings and options."""
    clear_output()
    hr = HDLRegression()
    hr.set_code_coverage(
        code_coverage_settings="bcestx",
        code_coverage_file="no_file.ucdb",
        merge_options="some_option",
    )
    assert hr.hdlcodecoverage.get_code_coverage_settings() == "bcestx"
    assert hr.hdlcodecoverage.get_options() == "some_option"


def test_remove_leading_hyphen(sim_env):
    """Test that leading hyphen is removed from coverage settings."""
    clear_output()
    hr = HDLRegression()
    hr.set_code_coverage(code_coverage_settings="-bcestx", code_coverage_file="no_file.ucdb")
    assert hr.hdlcodecoverage.get_code_coverage_settings() == "bcestx"


def test_illegal_character(sim_env, capsys):
    clear_output()
    hr = HDLRegression()
    coverage_settings = "bcuestx"  # 'u' is illegal for Modelsim
    hr.set_code_coverage(code_coverage_settings=coverage_settings, code_coverage_file="no_file.ucdb")
    hr.start()
    captured = capsys.readouterr()
    assert "Invalid coverage settings in: bcuestx" in captured.out
    # Value should still be stored
    assert hr.hdlcodecoverage.get_code_coverage_settings() is coverage_settings


def test_minimal_code_coverage_settings(sim_env):
    """Test that minimal code coverage settings are accepted."""
    clear_output()
    hr = HDLRegression()
    hr.set_code_coverage(code_coverage_settings="teb", code_coverage_file="no_file.ucdb")
    assert hr.hdlcodecoverage.get_code_coverage_settings() == "teb"


@pytest.mark.modelsim
def test_modelsimplaces_ucdb_in_coverage_folder(tmp_path, sim_env):
    """Test that code coverage file is placed in coverage folder under test path."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:    
        clear_output()
        hr = HDLRegression()
        proj = FakeProject(test_path=proj_abs(tmp_path / "hdlregression" / "test"))
        cc = hcov.ModelsimCodeCoverage(project=proj)

        cc.set_code_coverage_file("some/dir/coverage.ucdb")
        expect_dir = os.path.join(proj.settings.get_test_path(), "coverage")
        assert cc.get_code_coverage_file().startswith(os.path.abspath(expect_dir))
        assert cc.get_code_coverage_file().endswith("coverage.ucdb")


@pytest.mark.modelsim
def test_find_code_coverage_files_discovers_matching_ucdb(tmp_path, sim_env):
    """Test that code coverage files are discovered in test tree."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:    
        clear_output()
        test_root = tmp_path / "hdlregression" / "test"
        (test_root / "t1").mkdir(parents=True)
        (test_root / "t2").mkdir(parents=True)

        for d in ["t1", "t2"]:
            (test_root / d / "coverage.ucdb").write_text("dummy")

        proj = FakeProject(test_path=proj_abs(test_root))
        cc = hcov.ModelsimCodeCoverage(project=proj)
        cc.set_code_coverage_file("coverage.ucdb")

        assert cc._find_code_coverage_files() is True
        assert len(cc.file_list) == 2
        assert all(p.endswith("coverage.ucdb") for p in cc.file_list)


@pytest.mark.modelsim
def test_merge_builds_expected_vcover_command(tmp_path, monkeypatch, sim_env):
    """Test that merging code coverage files builds expected vcover command."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        test_root = tmp_path / "hdlregression" / "test"
        (test_root / "a").mkdir(parents=True)
        (test_root / "b").mkdir(parents=True)
        for d in ["a", "b"]:
            (test_root / d / "coverage.ucdb").write_text("dummy")

        proj = FakeProject(test_path=proj_abs(test_root))
        cc = hcov.ModelsimCodeCoverage(project=proj)
        cc.set_code_coverage_settings("bcst")
        cc.set_code_coverage_file("coverage.ucdb")
        cc.set_options("-testassociated")

        # Monkeypatch CommandRunner used in hdlcodecoverage module
        fake_runner = CaptureCommandRunner()
        monkeypatch.setattr(hcov, "CommandRunner", lambda project=None: fake_runner)

        # Find and merge
        cc._find_code_coverage_files()
        cc._merge_code_coverage_files()

        calls = fake_runner.captured
        assert len(calls) == 1
        cmd = calls[0]["cmd"]
        assert cmd[0] == "vcover" and cmd[1] == "merge"
        assert "-testassociated" in cmd
        assert any(p.endswith("/a/coverage.ucdb") for p in cmd)
        assert any(p.endswith("/b/coverage.ucdb") for p in cmd)
        assert "-out" in cmd
        out_idx = cmd.index("-out") + 1
        assert cmd[out_idx].endswith("_merge.ucdb")


@pytest.mark.modelsim
def test_apply_exceptions_builds_vsim_command(tmp_path, monkeypatch, sim_env):
    """Test that applying exceptions builds expected vsim command."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:    
        clear_output()
        test_root = tmp_path / "hdlregression" / "test"
        (test_root / "x").mkdir(parents=True)
        (test_root / "x" / "coverage.ucdb").write_text("dummy")

        proj = FakeProject(test_path=proj_abs(test_root), script_path=proj_abs(tmp_path))
        cc = hcov.ModelsimCodeCoverage(project=proj)
        cc.set_code_coverage_file("coverage.ucdb")

        exclude = tmp_path / "exclude.tcl"
        exclude.write_text("coverage exclude -du *third_party*")
        cc.set_exclude_file("exclude.tcl")

        fake_runner = CaptureCommandRunner()
        monkeypatch.setattr(hcov, "CommandRunner", lambda project=None: fake_runner)

        merged = cc._insert_to_code_coverage_file_name(cc.get_code_coverage_file(), "_merge")
        filtered = cc._apply_exceptions()

        cmd = fake_runner.captured[0]["cmd"]
        assert cmd[0] == "vsim"
        assert "-c" in cmd and "-viewcov" in cmd and merged in cmd
        assert any(("do {}".format(cc.get_exclude_file()) in x) for x in cmd)
        assert any(("coverage save" in x and "exit" in x) for x in cmd)
        assert filtered.endswith("_filter.ucdb")


@pytest.mark.modelsim
def test_generate_reports_issue_vcover_report(tmp_path, sim_env):
    """Test that generating reports issues expected vcover report commands."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        proj = FakeProject(test_path=proj_abs(tmp_path / "hdlregression" / "test"))
        cc = hcov.ModelsimCodeCoverage(project=proj)
        cc.set_code_coverage_settings("bcst")
        cc.set_code_coverage_file("coverage.ucdb")

        # These calls project.run_command (string) -> logs in proj.run_log
        merge_ucdb = cc._insert_to_code_coverage_file_name(cc.get_code_coverage_file(), "_merge")
        cc._generate_html_report(merge_ucdb)
        html_cmd = proj.run_log[-1]
        assert "vcover report" in html_cmd and "-html" in html_cmd
        assert "-code bcst" in html_cmd

        cc._generate_txt_report(merge_ucdb)
        txt_cmd = proj.run_log[-1]
        assert "vcover report" in txt_cmd and "-output" in txt_cmd
        assert txt_cmd.endswith(".txt " + merge_ucdb)


@pytest.mark.modelsim
def test_merge_code_coverage_no_files_returns_false(tmp_path, sim_env):
    """Test that merging code coverage with no files returns False."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:
        clear_output()
        proj = FakeProject(test_path=proj_abs(tmp_path / "hdlregression" / "test"))
        cc = hcov.ModelsimCodeCoverage(project=proj)
        cc.set_code_coverage_settings("bcst")
        cc.set_code_coverage_file("coverage.ucdb")
        # No files created → should return False
        assert cc.merge_code_coverage() is False
        assert any(
            lvl == "WARN" and "No code coverage files found" in msg
            for (lvl, msg) in proj.logger.messages
        )


@pytest.mark.modelsim
def test_merge_code_coverage_not_enabled_returns_true(tmp_path, sim_env):
    """Test that merging code coverage when not enabled returns True."""
    if not sim_env["modelsim"]:
        pytest.skip("Modelsim not installed")
    else:    
        clear_output()
        proj = FakeProject(test_path=proj_abs(tmp_path / "hdlregression" / "test"))
        cc = hcov.ModelsimCodeCoverage(project=proj)
        # code_coverage_file not set → coverage not enabled → True
        assert cc.merge_code_coverage() is True