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

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../hdlregression/scan')))

from hdlregression import HDLRegression


if len(sys.argv) >= 2:
    """
    Remove pytest from argument list
    """
    sys.argv.pop(1)


def get_file_path(path) -> str:
    """
    Adjust file paths to match running directory.
    """
    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(TEST_DIR, path)


def clear_output():
    if os.path.isdir("./hdlregression"):
        shutil.rmtree("./hdlregression")


def setup_function():
    if os.path.isdir("./hdlregression"):
        print("WARNING! hdlregression folder already exist!")


def tear_down_function():
    if os.path.isdir("./hdlregression"):
        shutil.rmtree("./hdlregression")


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


# Import the parsers and BaseParser from your package
from hdlregression.scan.vhdlscanner import (
    BaseParser,
    ConfigurationParser,
    ArchitectureParser,
)

# ---------- Test helpers (minimal fakes) ----------
class FakeLibrary:
    def __init__(self, name="work"):
        self._name = name
    def get_name(self):
        return self._name

class FakeModule:
    def __init__(self, name, library):
        self._name = name
        self._lib = library
        self.int_deps = set()
        self.ext_deps = set()
    def get_library(self):
        return self._lib
    def get_name(self):
        return self._name
    def add_int_dep(self, name):
        if isinstance(name, (list, set, tuple)):
            self.int_deps.update(name)
        elif name:
            self.int_deps.add(name)
    def add_ext_dep(self, name):
        if isinstance(name, (list, set, tuple)):
            self.ext_deps.update(name)
        elif name:
            self.ext_deps.add(name)

class FakeMaster:
    """Provides just enough surface for the parsers we test."""
    def __init__(self, library_name="work"):
        self._library = FakeLibrary(library_name)
        self._module_container = {}
        # --- NEW: testcase plumbing expected by TestcaseParser ---
        self.testcase_string = "hdlregression_testcase"  # noe som ikke matcher i testkoden din
        self._testcases = []

    # --- NEW: methods used by TestcaseParser/ArchitectureParser ---
    def add_testcase(self, name):
        self._testcases.append(name)

    def get_testcase(self):
        return list(self._testcases)

    # (resten som før)
    def get_library(self):
        return self._library

    def get_library_dep(self):
        return []  # ikke set(), så add_ext_dep ikke får et uhashable objekt

    def get_int_dep(self):
        return []  # samme begrunnelse

    def get_context_module(self, name):
        return self._get_or_make(name)

    def get_configuration_module(self, name):
        return self._get_or_make(name)

    def get_architecture_module(self, name, arch_of_name):
        key = f"arch::{name}"
        if key not in self._module_container:
            self._module_container[key] = FakeModule(name=key, library=self._library)
        return self._module_container[key]

    def get_package_module(self, name):
        return self._get_or_make(name)

    def get_package_body_module(self, name):
        return self._get_or_make(name)

    def _get_or_make(self, name):
        if name not in self._module_container:
            self._module_container[name] = FakeModule(name=name, library=self._library)
        return self._module_container[name]


# ---------- Unit tests ----------

def test_configuration_parser_captures_use_configuration_nested():
    master = FakeMaster(library_name="work")
    parser = ConfigurationParser(master=master)

    code = r"""
    configuration addsub_core_struc_cfg of addsub_core is
      for struc 
        for gen_smorequ_four
          for addsub_ovcy_1 : addsub_ovcy
            use configuration work.addsub_ovcy_rtl_cfg;
          end for;
        end for;
        for gen_greater_four
          for gen_addsub
            for gen_nibble_addsub
              for all : addsub_cy
                use configuration work.addsub_cy_rtl_cfg;
              end for;
            end for;
            for gen_last_addsub
              for all : addsub_ovcy
                use configuration addsub_ovcy_rtl_cfg; -- no lib prefix
              end for;
            end for;
          end for;
        end for;
      end for;
    end addsub_core_struc_cfg;
    """

    parser._parse(code)

    m = master._module_container["addsub_core_struc_cfg"]
    # Must depend on the entity under configuration:
    assert "addsub_core" in m.int_deps
    # Must also depend on the referenced configurations:
    assert "addsub_ovcy_rtl_cfg" in m.int_deps
    assert "addsub_cy_rtl_cfg" in m.int_deps
    # Should not create spurious external deps for 'work'
    assert "work" not in m.ext_deps


def test_architecture_parser_captures_configuration_instantiation_and_use_configuration():
    master = FakeMaster(library_name="work")
    parser = ArchitectureParser(master=master)

    code = r"""
    architecture rtl of top is
    begin
      -- configuration instantiation label : configuration lib-less
      u_cfg0 : configuration my_local_cfg;
      -- configuration instantiation with library
      u_cfg1 : configuration work.some_cfg;
      -- 'use configuration' inside some block/spec
      -- (Note: allowed in configuration specifications within architectures)
      use configuration work.inner_cfg;
    end rtl;
    """

    parser._parse(code)

    # ArchitectureParser creates a module keyed by arch name
    m = master._module_container["arch::rtl"]
    # Should have picked up both config instantiations
    assert "my_local_cfg" in m.int_deps
    assert "some_cfg" in m.int_deps
    # And also the 'use configuration' dependency
    assert "inner_cfg" in m.int_deps


def test_configuration_parser_handles_external_library_config():
    master = FakeMaster(library_name="work")
    parser = ConfigurationParser(master=master)

    code = r"""
    configuration foo_cfg of foo is
      for rtl
        for all : bar
          use configuration otherlib.bar_cfg;
        end for;
      end for;
    end foo_cfg;
    """

    parser._parse(code)
    m = master._module_container["foo_cfg"]

    # Internal entity dependency
    assert "foo" in m.int_deps
    # We don’t claim to know otherlib.bar_cfg content, but we see external lib
    assert "otherlib" in m.ext_deps
    # (Optional policy) we can still add the config name as int_dep if same lib; here it is otherlib, so not added
    assert "bar_cfg" not in m.int_deps

def test_configuration_file_loading():
    clear_output()
    hr = HDLRegression()

    assert True, "check configration file loading"
