#
# Copyright (c) 2022 by HDLRegression Authors.  All rights reserved.
# Licensed under the MIT License; you may not use this file except in compliance with the License.
# You may obtain a copy of the License at https://opensource.org/licenses/MIT.
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.
#
# HDLRegression AND ANY PART THEREOF ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH UVVM OR THE USE OR OTHER DEALINGS IN HDLRegression.
#

import os
import platform
import datetime
import subprocess
from abc import ABC, abstractmethod


class SettingsError(Exception):
    pass


class ItemExistError(SettingsError):
    pass


class InvalidPathError(SettingsError):
    pass

class UnsupportedMethodError(SettingsError):
    pass

class UnavailableSimulatorError(SettingsError):
    pass

class HDLRegressionSettings:
    SIM_WAVE_FILE_FORMAT = ["FST", "VCD", "GHW"]

    def __init__(self):
        self.hdlregression_version = "0.0.0"
        self.compile_time = 0
        self.os_platform = platform.system().lower()
        self.verbosity = False
        self.gui_mode = False
        self.full_regression = False
        self.stop_on_failure = False
        self.time_of_run = None
        self.run_success = None
        self.sim_success = False
        self.sim_time = None
        self.threading = False
        self.num_threads = 0
        self.no_sim = False
        self.no_compile = False
        self.show_err_warn_output = False
        self.use_log_color = True

        self.python_exec = None

        self.netlist_timing = None

        self.sim_path = None
        self.src_path = None
        self.script_path = None
        self.output_path = "./hdlregression"

        self.library_compile_list = []
        self.library_name = "my_work_lib"
        self.debug_mode = None
        self.force_recompile = False
        self.clean = False
        self.keep_code_coverage = False
        self.cli_override = False
        self.testcase = None
        self.testcase_list = None
        self.testgroup = None
        self.logger_level = "info"
        self.testcase_identifier_name = "gc_testcase"
        self.wlf_dunmp_enable = False

        self.list_testcase = False
        self.export_testcases_json_path = None
        self.list_compile_order = False
        self.list_testgroup = False
        self.list_dependencies = False

        self.result_check_str = None
        self.return_code = 0

        self.gui_compile_all = False
        self.gui_compile_changes = False
        self.simulator_wave_file_format = "vcd"  # Default for GHDL and NVC.
        
        # Initialize a available simulator settings obj
        self.simulator_cli_select = False
        self.simulator_detector = SimulatorDetector()
        self.simulator_info = self.simulator_detector.get_simulators_info()
        self.simulator_settings = self.simulator_detector.get_simulator_settings_object(self.simulator_info.get("simulator_name"))

        self.libraries = []

        self.ignored_simulator_exit_codes = []

    def detect_python_exec(self):
        """ Detects the python executable to use """
        python_executables = ["python3", "python", "Python3", "Python"]
    
        for executable in python_executables:
            try:
                output = (subprocess.check_output([executable, "--version"], stderr=subprocess.STDOUT).decode().strip())
                if "Python 3" in output:
                    self.python_exec = executable
                    return
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue        

        self.python_exec = "python"

    def get_python_exec(self) -> str:
        if self.python_exec is None:
            self.python_exec = self.detect_python_exec()
        return self.python_exec

    def set_return_code(self, return_code: int):
        self.return_code = return_code

    def get_return_code(self) -> int:
        return self.return_code

    def set_hdlregression_version(self, version):
        self.hdlregression_version = version

    def get_hdlregression_version(self) -> str:
        return self.hdlregression_version

    def set_src_path(self, path):
        """
        HDLRegression install path
        """
        self.src_path = path

    def get_src_path(self) -> str:
        return self.src_path

    def set_sim_path(self, path):
        """
        Path calling regression script
        """
        self.sim_path = path

    def get_sim_path(self):
        return self.sim_path

    def set_script_path(self, path):
        """
        Regression script path
        """
        self.script_path = path

    def get_script_path(self) -> str:
        return self.script_path

    def reset_library_compile(self):
        self.library_compile_list = []

    def add_library_compile(self, library):
        if library not in self.library_compile_list:
            self.library_compile_list.append(library)

    def get_library_compile(self) -> list:
        return self.library_compile_list

    def check_library_in_compile_list(self, library) -> bool:
        return library in self.library_compile_list

    def set_compile_time(self, compile_time):
        if compile_time > self.compile_time:
            self.compile_time = compile_time

    def get_compile_time(self):
        return self.compile_time

    def get_os_platform(self):
        return self.os_platform

    def set_verbose(self, verbosity):
        self.verbosity = verbosity

    def get_verbose(self) -> bool:
        return self.verbosity

    def set_gui_mode(self, gui_mode):
        self.gui_mode = gui_mode

    def get_gui_mode(self) -> bool:
        return self.gui_mode

    def set_use_log_color(self, use_log_color):
        self.use_log_color = use_log_color

    def get_use_log_color(self) -> bool:
        return self.use_log_color

    def set_wlf_dump_enable(self, enable):
        self.wlf_dunmp_enable = enable

    def get_wlf_dump_enable(self) -> bool:
        return self.wlf_dunmp_enable
    # ----------------------------------
    # Threading
    # ----------------------------------
    def set_threading(self, enable) -> None:
        self.threading = enable

    def get_threading(self) -> bool:
        return self.threading

    def set_num_threads(self, num_threads) -> None:
        self.num_threads = num_threads

    def get_num_threads(self) -> int:
        return self.num_threads

    # ----------------------------------
    # Running
    # ----------------------------------

    # -- compilation status
    def set_run_success(self, success):
        self.run_success = success

    def get_run_success(self) -> bool:
        return self.run_success

    # --- simulation status
    def set_sim_success(self, success: bool):
        self.sim_success = success

    def get_sim_success(self) -> bool:
        return self.sim_success

    # ------------------------------
    def get_run_all(self) -> bool:
        return self.full_regression

    def set_stop_on_failure(self, stop_on_failure):
        self.stop_on_failure = stop_on_failure

    def get_stop_on_failure(self) -> bool:
        return self.stop_on_failure

    def set_time_of_run(self):
        time_of_run = datetime.datetime.now()
        self.time_of_run = time_of_run.strftime("%Y-%m-%d_%H.%M.%S.%f")

    def get_time_of_run(self):
        return self.time_of_run

    def set_sim_time(self, sim_time):
        self.sim_time = sim_time

    def get_sim_time(self) -> str:
        return self.sim_time

    def set_output_path(self, output_path):
        self.output_path = output_path

    def get_output_path(self) -> str:
        return self.output_path

    def get_library_path(self) -> str:
        return os.path.join(self.get_output_path(), "library")

    def get_test_path(self) -> str:
        return os.path.join(self.get_output_path(), "test")

    def set_library_name(self, library_name):
        self.library_name = library_name

    def get_library_name(self) -> str:
        return self.library_name

    def set_modelsim_ini(self, modelsim_ini):
        self.simulator_settings.set_modelsim_ini(modelsim_ini)

    def get_modelsim_ini(self) -> str:
        return self.simulator_settings.get_modelsim_ini()

    def set_libraries(self, libraries):
        self.libraries = libraries

    def get_libraries(self) -> list:
        return self.libraries

    def set_debug_mode(self, debug_mode):
        self.debug_mode = debug_mode

    def get_debug_mode(self):
        return self.debug_mode

    def set_force_recompile(self, force_recompile):
        self.force_recompile = force_recompile

    def get_force_recompile(self) -> bool:
        return self.force_recompile

    def set_clean(self, clean):
        self.clean = clean

    def get_clean(self) -> bool:
        return self.clean

    def set_cli_override(self, cli_override=True):
        self.cli_override = cli_override

    def get_cli_override(self) -> bool:
        return self.cli_override

    def set_ignored_simulator_exit_codes(self, codes):
        self.ignored_simulator_exit_codes = codes

    def get_ignored_simulator_exit_codes(self) -> list:
        return self.ignored_simulator_exit_codes

    # ----------------------------------
    # Logging / reporting
    # ----------------------------------
    def set_logger_level(self, logger_level):
        self.logger_level = logger_level

    def get_logger_level(self):
        return self.logger_level

    def set_list_compile_order(self, list_compile_order):
        self.list_compile_order = list_compile_order

    def get_list_compile_order(self) -> bool:
        return self.list_compile_order

    def set_list_dependencies(self, enable=True):
        self.list_dependencies = enable

    def get_list_dependencies(self) -> bool:
        return self.list_dependencies

    def set_show_err_warn_output(self, enable):
        self.show_err_warn_output = enable

    def get_show_err_warn_output(self) -> bool:
        return self.show_err_warn_output

    def set_wlf_dunmp_enable(self, enable):
        self.wlf_dunmp_enable = enable

    def get_wlf_dump_enable(self) -> bool:
        return self.wlf_dunmp_enable
    
    # ----------------------------------
    # Test group
    # ----------------------------------
    def set_list_testgroup(self, list_testgroup):
        self.list_testgroup = list_testgroup

    def get_list_testgroup(self) -> bool:
        return self.list_testgroup

    def set_testgroup(self, testgroup):
        self.testgroup = testgroup

    def get_testgroup(self) -> str:
        return self.testgroup

    # ----------------------------------
    # Testcase
    # ----------------------------------
    def set_result_check_str(self, result_check_str):
        self.result_check_str = result_check_str

    def get_result_check_str(self) -> str:
        return self.result_check_str

    def set_testcase_identifier_name(self, testcase_identifier_name):
        self.testcase_identifier_name = testcase_identifier_name

    def get_testcase_identifier_name(self) -> str:
        return self.testcase_identifier_name

    def set_list_testcase(self, list_testcase):
        self.list_testcase = list_testcase

    def get_list_testcase(self) -> bool:
        return self.list_testcase
    
    def get_export_testcases_json_path(self) -> str:
        return self.export_testcases_json_path
    
    def set_export_testcases_json_path(self, json_path):
        if isinstance(json_path, str):
            self.export_testcases_json_path = json_path.lower()

    def set_testcase(self, testcase):
        """
        Stores testcase.
        Params:
            testcase(str) : entity.architecture.sequencer_testcase
        """
        if testcase:
            # Remove trailing whitespace
            testcase = testcase.strip()

            # Convert to list
            if isinstance(testcase, list):
                testcase = testcase[0].split(".")
            elif isinstance(testcase, str):
                testcase = testcase.split(".")
            else:
                raise TypeError(f"testcase type not supported: {testcase}")

            if len(testcase) == 1:
                testcase = [testcase[0], None, None]
            elif len(testcase) == 2:
                testcase = [testcase[0], testcase[1], None]
            self.testcase = testcase
            self.add_to_testcase_list(testcase)

        else:
            self.testcase = None
            self.empty_testcase_list()

    def get_testcase(self) -> list:
        return self.testcase

    def add_to_testcase_list(self, testcase) -> None:
        if not self.testcase_list:
            self.testcase_list = []
        if testcase not in self.testcase_list:
            self.testcase_list.append(testcase)

    def empty_testcase_list(self) -> None:
        self.testcase = None
        self.testcase_list = None

    def get_testcase_list(self) -> list:
        return self.testcase_list

    # ----------------------------------
    # Simulator
    # ----------------------------------

    def get_simulator_settings(self):
        return self.simulator_settings

    def get_simulators_info(self) -> dict:
        return self.simulator_info

    def set_simulator_name(self, simulator_name, cli=False):
        if cli is True or self.simulator_cli_select is False:
            self.simulator_settings = self.simulator_detector.get_simulator_settings_object(simulator_name)
            if cli is True:
                self.simulator_cli_select = True

    def get_simulator_name(self) -> str:
        return self.simulator_settings.get_simulator_name()

    def set_simulator_path(self, path):
        if path is not None:
            self.simulator_settings.set_simulator_path(path)

    def get_simulator_path(self) -> str:
        return self.simulator_settings.get_simulator_path()

    def get_simulator_exec(self, sim_exec) -> str:
        return self.simulator_settings.get_simulator_exec(sim_exec)

    def set_com_options(self, com_options=None, hdl_lang=None):
        self.simulator_settings.set_com_options(
            com_options=com_options, hdl_lang=hdl_lang
        )

    def get_com_options(self, hdl_lang="vhdl"):
        return self.simulator_settings.get_com_options(hdl_lang=hdl_lang)

    def remove_com_options(self):
        self.simulator_settings.remove_com_options()

    def get_is_default_com_options(self) -> bool:
        return self.simulator_settings.get_is_default_com_options()

    def set_sim_options(self, options) -> None:
        self.simulator_settings.set_sim_options(options=options)

    def get_sim_options(self) -> list:
        return self.simulator_settings.get_sim_options()
    
    def set_runtime_options(self, options) -> None:
        self.simulator_settings.set_runtime_options(options)

    def get_runtime_options(self) -> list:
        return self.simulator_settings.get_runtime_options()
    
    def set_global_options(self, options) -> None:
        self.simulator_settings.set_global_options(options)

    def get_global_options(self) -> list:
        return self.simulator_settings.get_global_options()

    def set_elaboration_options(self, options) -> None:
        self.simulator_settings.set_elaboration_options(options)

    def get_elaboration_options(self) -> list:
        return self.simulator_settings.get_elaboration_options()
 
    def add_sim_options(self, options, warning=True):
        self.simulator_settings.add_sim_options(options, warning)

    def set_no_sim(self, no_sim=False):
        self.no_sim = no_sim

    def get_no_sim(self) -> bool:
        return self.no_sim

    def set_no_compile(self, no_compile=False):
        self.no_compile = no_compile

    def get_no_compile(self) -> bool:
        return self.no_compile

    def set_run_all(self, full_regression):
        self.full_regression = full_regression

    # ----------------------------------
    # Gui
    # ----------------------------------
    def set_gui_compile_all(self, enabled=True):
        self.gui_compile_all = enabled

    def get_gui_compile_all(self) -> bool:
        return self.gui_compile_all

    def set_gui_compile_changes(self, enabled=True):
        self.gui_compile_changes = enabled

    def get_gui_compile_changes(self) -> bool:
        return self.gui_compile_changes

    def get_is_gui_mode(self) -> bool:
        return self.get_gui_compile_all() or self.get_gui_compile_changes()

    def set_simulator_wave_file_format(self, file_format):
        if isinstance(file_format, str):
            if file_format.upper() in self.SIM_WAVE_FILE_FORMAT:
                self.simulator_wave_file_format = file_format.lower()

    def get_simulator_wave_file_format(self) -> str:
        return self.simulator_wave_file_format

    # ----------------------------------
    # Netlist
    # ----------------------------------
    def set_netlist_timing(self, netlist_timing):
        self.netlist_timing = netlist_timing

    def get_netlist_timing(self) -> str:
        return self.netlist_timing

    # ----------------------------------
    # Code Coverage
    # ----------------------------------
    def set_keep_code_coverage(self, keep_code_coverage):
        self.keep_code_coverage = keep_code_coverage

    def get_keep_code_coverage(self) -> bool:
        return self.keep_code_coverage

class SimulatorDetector:

    ID_MODELSIM_SIMULATOR = ["modelsim", "MODELSIM", "mentor", "MENTOR", "questa", "QUESTA"]
    ID_RIVIERA_SIMULATOR = [
        "riviera",
        "RIVIERA",
        "riviera-pro",
        "RIVIERA-PRO",
    ]
    ID_ACTIVE_HDL_SIMULATOR = ["active-hdl", "ACTIVE-HDL", "active", "ACTIVE"]
    ID_GHDL_SIMULATOR = ["ghdl", "GHDL"]
    ID_NVC_SIMULATOR = ["nvc", "NVC"]
    ID_VIVADO_SIMULATOR = ["vivado", "VIVADO"]


    def __init__(self):
        self.simulator_info = self.get_simulators_info()

    @staticmethod
    def is_simulator_installed(
        simulator_call: str, version_call: str = "--version", simulator_name: str = None
    ) -> bool:
        try:
            # Capturing the output instead of sending it to DEVNULL
            result = subprocess.run(
                [simulator_call, version_call],
                check=True,
                stdout=subprocess.PIPE,  # Capture stdout
                stderr=subprocess.PIPE,  # Capture stderr to handle any error messages
                universal_newlines=True,  # Ensure the output is returned as a string
            )
            if simulator_name:
                # Check if the simulator name is in the output
                if simulator_name.lower() in result.stdout.lower():
                    return True
            else:
                if simulator_call.lower() in result.stdout.lower():
                    return True
            return False
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_simulators_info(self) -> dict:
        platform_info = platform.system()
        modelsim_installed = self.is_simulator_installed(
            simulator_call="vsim", version_call="-version"
        )
        ghdl_installed = self.is_simulator_installed(
            simulator_call="ghdl", version_call="--version"
        )
        nvc_installed = self.is_simulator_installed(
            simulator_call="nvc", version_call="--version"
        )
        riviera_pro_installed = self.is_simulator_installed(
            simulator_call="vsimsa", version_call="-version", simulator_name="riviera"
        )
        active_hdl_installed = self.is_simulator_installed(
            simulator_call="vsim", version_call="-version", simulator_name="active-hdl")
        vivado_installed = self.is_simulator_installed(
            simulator_call="xsim", version_call="--version", simulator_name="vivado"
        )

        # Determine which simulator is currently set as default
        simulator = ""
        if modelsim_installed:
            simulator = "MODELSIM"
        elif nvc_installed:
            simulator = "NVC"
        elif ghdl_installed:
            simulator = "GHDL"
        elif riviera_pro_installed:
            simulator = "RIVIERA-PRO"
        elif active_hdl_installed:
            simulator = "ACTIVE-HDL"
        elif vivado_installed:
            simulator = "VIVADO"

        return {
            "platform": platform_info,
            "MODELSIM": modelsim_installed,
            "NVC": nvc_installed,
            "GHDL": ghdl_installed,
            "RIVIERA-PRO": riviera_pro_installed,
            "ACTIVE-HDL": active_hdl_installed,
            "VIVADO": vivado_installed,
            "simulator_name": simulator,
        }

    def _validate_simulator_name(self, simulator_name) -> str:
        if simulator_name in self.ID_MODELSIM_SIMULATOR:
            return "MODELSIM"
        elif simulator_name in self.ID_RIVIERA_SIMULATOR:
            return "RIVIERA-PRO"
        elif simulator_name in self.ID_ACTIVE_HDL_SIMULATOR:
            return "ACTIVE-HDL"
        elif simulator_name in self.ID_GHDL_SIMULATOR:
            return "GHDL"
        elif simulator_name in self.ID_NVC_SIMULATOR:
            return "NVC"
        elif simulator_name in self.ID_VIVADO_SIMULATOR:
            return "VIVADO"
        else:
            if simulator_name is None or simulator_name == "":
                raise UnavailableSimulatorError("Simulator name missing: '{}'.".format(simulator_name))
            else:
                raise UnavailableSimulatorError("Simulator '{}' unsupported.".format(simulator_name))
        
    def _validate_simulator_installed(self, simulator_name) -> None:
        """Check with simulator info dict if the simulator name is found/installed"""
        if self.simulator_info.get(simulator_name) is False:
            raise UnavailableSimulatorError("Simulator {} not found.".format(simulator_name))
    
    def get_simulator_settings_object(self, simulator_name) -> "SimulatorSettings":
        """Detects available simulator and returns a simulator settings obj."""

        sim_name = self._validate_simulator_name(simulator_name.upper())

        self._validate_simulator_installed(sim_name)

        if sim_name == "MODELSIM": return ModelsimSettings()
        elif sim_name == "RIVIERA-PRO": return RivieraProSettings()
        elif sim_name == "ACTIVE-HDL": return ActiveHDLSettings()
        elif sim_name == "NVC": return NVCSettings()
        elif sim_name == "GHDL": return GHDLSettings()
        elif sim_name == "VIVADO": return VivadoSettings()
        elif sim_name == "ACTIVE-HDL": return ActiveHDLSettings()
        else: raise UnavailableSimulatorError("Simulator {} not found.".format(sim_name))


class TestcaseSettings:
    def __init__(self):
        self.copy_file = {}

    def copy_file_to_testcase_folder(self, filename: str, testcase: str) -> None:
        testcase = testcase.lower()
        if testcase in self.copy_file:
            self.copy_file[testcase].append(filename)
        else:
            self.copy_file[testcase] = [filename]

    def get_copy_file_to_testcase_folder(self, testcase: str) -> list:
        return self.copy_file.get(str(testcase), [])


class SimulatorSettings(ABC):

    SIMULATOR_NAME = None
    DEF_COM_OPTIONS_VHDL = []
    DEF_COM_OPTIONS_VERILOG = []
    DEF_SIM_OPTIONS = []
    DEF_RUNTIME_OPTIONS = []
    DEF_GLOBAL_OPTIONS = []
    DEF_ELABORATION_OPTIONS = []

    def __init__(self):
        self.cli_selected_simulator = False
        self.simulator_path = None
        self.modelsim_ini = "modelsim.ini"
        self.simulator_name = self.SIMULATOR_NAME
        self.sim_options = self.DEF_SIM_OPTIONS
        self.runtime_options = self.DEF_RUNTIME_OPTIONS
        self.global_options = self.DEF_GLOBAL_OPTIONS
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.elaboration_options = self.DEF_ELABORATION_OPTIONS

    def get_simulator_name(self) -> str:
        if self.simulator_name:
            return self.simulator_name
        else:
            sim_info = self.get_simulators_info()
            return sim_info.get("simulator")

    def set_com_options(self, com_options=None, hdl_lang=None):
        if hdl_lang == "vhdl":
            self.com_options_vhdl = com_options
        elif hdl_lang == "verilog":
            self.com_options_verilog = com_options
        else:
            self.com_options_vhdl = com_options
            self.com_options_verilog = com_options

    def get_com_options(self, hdl_lang="vhdl"):
        if hdl_lang == "vhdl":
            return self.com_options_vhdl
        elif hdl_lang == "verilog":
            return self.com_options_verilog

    def remove_com_options(self):
        self.com_options_vhdl = []
        self.com_options_verilog = []

    @abstractmethod
    def get_is_default_com_options(self) -> bool:
        pass

    def set_runtime_options(self, options) -> None:
        pass

    def get_runtime_options(self) -> list:
        pass

    def set_global_options(self, options) -> None:
        pass

    def get_global_options(self) -> list:
        pass

    def set_elaboration_options(self, options) -> None:
        pass

    def get_elaboration_options(self) -> list:
        pass

    def set_sim_options(self, options) -> None:
        if isinstance(options, str):
            self.sim_options = list(options.strip().split(" "))
        elif isinstance(options, list):
            self.sim_options = options
        else:
            if options:
                raise TypeError(
                    "sim_options parameter needs to be given as a list or a string"
                )

    def add_sim_options(self, options, warning=True):
        for item in self.sim_options:
            if options in item:
                if warning is True:
                    raise ItemExistError("sim_options %s already set." % (options))
                return
        self.sim_options.append(options)

    def get_sim_options(self) -> list:
        return self.sim_options

    def set_simulator_path(self, path):
        if path is None or os.path.isdir(path) is False:
            raise InvalidPathError("Simulator exec %s not valid." % (path))
        else:
            self.simulator_path = path

    def get_simulator_path(self) -> str:
        return self.simulator_path

    def get_simulator_exec(self, sim_exec) -> str:
        if self.simulator_path is not None:
            sim_exec = os.path.join(self.simulator_path, sim_exec)
            return sim_exec
        else:
            return sim_exec

    def set_modelsim_ini(self, modelsim_ini):
        raise UnsupportedMethodError("Method not supported by simulator '{}'.".format(self.simulator_name))

    def get_modelsim_ini(self) -> str:
        raise UnsupportedMethodError("Method not supported by simulator '{}'.".format(self.simulator_name))


class ModelsimSettings(SimulatorSettings):
    SIMULATOR_NAME = "MODELSIM"
    DEF_COM_OPTIONS_VHDL = ["-suppress", "1346,1236,1090", "-2008"]
    DEF_COM_OPTIONS_VERILOG = ["-vlog01compat"]

    def __init__(self):
        super().__init__()
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.sim_options = self.DEF_SIM_OPTIONS

    def get_is_default_com_options(self) -> bool:
        vhdl_default = self.com_options_verilog == self.DEF_COM_OPTIONS_VERILOG
        verilog_default = self.com_options_vhdl == self.DEF_COM_OPTIONS_VHDL
        return (vhdl_default is True) and (verilog_default is True)

    def set_modelsim_ini(self, modelsim_ini):
        self.modelsim_ini = modelsim_ini

    def get_modelsim_ini(self) -> str:
        return self.modelsim_ini


class NVCSettings(SimulatorSettings):
    SIMULATOR_NAME = "NVC"
    DEF_COM_OPTIONS_VHDL = ["--relaxed"]
    DEF_GLOBAL_OPTIONS = ["--stderr=error", "--messages=compact", "-M64m", "-H64m"]
    DEF_RUNTIME_OPTIONS = []
    DEF_ELABORATION_OPTIONS = ["-e", "--no-save", "--jit"]

    def __init__(self):
        super().__init__()
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.sim_options = self.DEF_SIM_OPTIONS
        self.runtime_options = self.DEF_RUNTIME_OPTIONS

    def get_is_default_com_options(self) -> bool:
        vhdl_default = self.com_options_verilog == self.DEF_COM_OPTIONS_VERILOG
        verilog_default = self.com_options_vhdl == self.DEF_COM_OPTIONS_VHDL
        return (vhdl_default is True) and (verilog_default is True)
    
    def set_runtime_options(self, options) -> None:
        if not isinstance(options, list):
            ValueError("Wrong paramteter type {} for 'set_runtime_options([list])'".format(type(options)))
        else:
            if self.runtime_options == self.DEF_RUNTIME_OPTIONS:        
                self.runtime_options = options

    def get_runtime_options(self) -> list:
        return self.runtime_options
    
    def set_global_options(self, options) -> None:
        if not isinstance(options, list):
            ValueError("Wrong paramteter type {} for 'set_global_options([list])'".format(type(options)))
        else:
            if self.global_options == self.DEF_GLOBAL_OPTIONS:        
                self.global_options = options

    def get_global_options(self) -> list:
        return self.global_options
    
    def set_elaboration_options(self, options) -> None:
        if not isinstance(options, list):
            ValueError("Wrong paramteter type {} for 'set_elab_options([list])'".format(type(options)))
        else:
            if self.elaboration_options == self.DEF_ELABORATION_OPTIONS:
                self.elaboration_options = options

    def get_elaboration_options(self) -> list:
        return self.elaboration_options


class GHDLSettings(SimulatorSettings):
    SIMULATOR_NAME = "GHDL"
    DEF_COM_OPTIONS_VHDL = [
        "--std=08",
        "--ieee=standard",
        "-frelaxed-rules",
        "--warn-no-shared",
        "--warn-no-hide",
    ]

    def __init__(self):
        super().__init__()
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.sim_options = self.DEF_SIM_OPTIONS

    def get_is_default_com_options(self) -> bool:
        vhdl_default = self.com_options_verilog == self.DEF_COM_OPTIONS_VERILOG
        verilog_default = self.com_options_vhdl == self.DEF_COM_OPTIONS_VHDL
        return (vhdl_default is True) and (verilog_default is True)

class RivieraProSettings(SimulatorSettings):
    SIMULATOR_NAME = "RIVIERA-PRO"
    DEF_COM_OPTIONS_VHDL = [
        "-2008",
        "-nowarn",
        "COMP96_0564",
        "-nowarn",
        "COMP96_0048",
        "-nowarn",
        "DAGGEN_0001",
    ]

    DEF_COM_OPTIONS_VERILOG = ["-vlog01compat"]

    def __init__(self):
        super().__init__()
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.sim_options = self.DEF_SIM_OPTIONS

    def get_is_default_com_options(self) -> bool:
        vhdl_default = self.com_options_verilog == self.DEF_COM_OPTIONS_VERILOG
        verilog_default = self.com_options_vhdl == self.DEF_COM_OPTIONS_VHDL
        return (vhdl_default is True) and (verilog_default is True)

class ActiveHDLSettings(RivieraProSettings):
    SIMULATOR_NAME = "ACTIVE-HDL"
    DEF_COM_OPTIONS_VHDL = [
        "-2008",
        "-nowarn",
        "COMP96_0564",
        "-nowarn",
        "COMP96_0048",
        "-nowarn",
        "DAGGEN_0001",
    ]
    DEF_COM_OPTIONS_VERILOG = ["-vlog01compat"]

    def __init__(self):
        super().__init__()
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.sim_options = self.DEF_SIM_OPTIONS

    def get_is_default_com_options(self) -> bool:
        vhdl_default = self.com_options_verilog == self.DEF_COM_OPTIONS_VERILOG
        verilog_default = self.com_options_vhdl == self.DEF_COM_OPTIONS_VHDL
        return (vhdl_default is True) and (verilog_default is True)

class VivadoSettings(SimulatorSettings):
    SIMULATOR_NAME = "VIVADO"
    DEF_COM_OPTIONS_VHDL = ["--2008"]

    def __init__(self):
        super().__init__()
        self.com_options_verilog = self.DEF_COM_OPTIONS_VERILOG
        self.com_options_vhdl = self.DEF_COM_OPTIONS_VHDL
        self.sim_options = self.DEF_SIM_OPTIONS

    def get_is_default_com_options(self) -> bool:
        vhdl_default = self.com_options_verilog == self.DEF_COM_OPTIONS_VERILOG
        verilog_default = self.com_options_vhdl == self.DEF_COM_OPTIONS_VHDL
        return (vhdl_default is True) and (verilog_default is True)
