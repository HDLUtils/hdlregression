#
# Copyright (c) 2022 by HDLRegression Authors.  All rights reserved.
# Licensed under the MIT License; you may not use this file except in
# compliance with the License.
# You may obtain a copy of the License at https://opensource.org/licenses/MIT.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# HDLRegression AND ANY PART THEREOF ARE PROVIDED "AS IS", WITHOUT WARRANTY OF
# ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH UVVM OR THE USE OR OTHER
# DEALINGS IN HDLRegression.
#

from . import __version__
from .hdlcodecoverage import *
from .arg_parser import arg_parser_reader
from .hdlregression_pkg import *
from .report.logger import Logger
from .settings import HDLRegressionSettings
from .settings import TestcaseSettings
from .construct.container import Container
from .report.jsonreporter import JSONReporter
from .report.csvreporter import CSVReporter
from .report.txtreporter import TXTReporter
from .report.xmlreporter import XMLReporter
from .report.htmlreporter import HTMLReporter
from .run.tcl_runner import TclRunnerModelsim, TclRunnerRiviera, TclRunnerActiveHDL
from .run.cmd_runner import CommandRunner
from .run.runner_modelsim import ModelsimRunner
from .run.runner_nvc import NVCRunner
from .run.runner_ghdl import GHDLRunner
from .run.runner_aldec import RivieraRunner, ActiveHDLRunner
from .run.vivado_runner import VivadoRunner
from .construct.hdllibrary import HDLLibrary, PrecompiledLibrary
from .configurator import SettingsConfigurator
from .run.hdltests import TestStatus
import copy
import sys
import os
import pickle
from signal import signal, SIGINT

# Enable terminal colors on windows OS
if os.name == "nt":
    from ctypes import windll

    k = windll.kernel32
    k.SetConsoleMode(k.GetStdHandle(-11), 7)
    os.system("color")

# Path from where regression script is called
sim_path = os.getcwd()
# HDLRegression installation path
src_path = os.path.dirname(os.path.abspath(__file__))
# Regression script path
script_path = os.path.abspath(sys.path[0])


class HDLRegression:
    """
    HDLRegression is a HDL regression testing tool for automating,
    and speeding up HDL simulations.

    The regression tool is especially greate for simulating
    testcases developed using UVVM, but UVVM is not required
    to run the regression tool.
    """

    # pylint: disable=consider-using-f-string
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-public-methods

    def __init__(
        self,
        simulator: str = None,
        init_from_gui: bool = False,
        arg_parser=None,
        output_path: str = None,
    ):
        """
        Initializes the HDLRegression class which provides a set
        of API methods for controlling the regression flow.

        :param simulator: Simulator to use for regression run
        :type simulator: str
        :param init_from_gui: Regression initialized in from GUI tcl call.
        :type init_from_gui: bool
        :param output_path: Path to store output and configuration
        :type output_path: str
        """
        self.init_from_gui = init_from_gui
        self.settings = self._initialize_settings(arg_parser)
        self.logger = self._initialize_logger()
        self.hdlcodecoverage = self._initialize_hdl_code_coverage()

        self.cached_simulator_settings = None

        self._initialize_signal_handler()
        if output_path is None:
            output_path = self.settings.get_output_path()
        self._load_project_data(output_path)
        self._set_simulator(sim_name=simulator)
        self._setup_logger()
        self.reporter = None
        self.testcase_settings = TestcaseSettings()
        self.settings.detect_python_exec()

    def add_precompiled_library(self, compile_path: str, library_name: str):
        """
        Adds a precompiled library to the structure.
        Precompiled library file reference is added to Modelsim.ini

        :param compile_path: Path pointing to the precompiled library.
        :type compile_path: str
        :param library_name: Name of a precompiled library that is not to
                             be parsed.
        :type library_name: str
        """
        validate_path(project=self, path=compile_path)
        lib = self._get_library_object(library_name=library_name, precompiled=True)
        lib.set_compile_path(compile_path)

    def add_files(
        self,
        filename: str,
        library_name: str = None,
        hdl_version: str = None,
        com_options: str = None,
        parse_file=True,
        netlist_inst: str = None,
        code_coverage: bool = False,
    ):
        """
        Add files to HDLRegression file list:
        1. Get a new or existing library object
        2. Pass filename to library object which will create file objects.

        :param filename; Name of file to be added to library
        :type filename: str
        :param library_name: Name of library to add file
        :type library_name: str
        :param hdl_version: VHDL version to use with file
        :type hdl_version: str
        :param com_options: Compile options to use with file
        :type com_options: str
        :param parse_file: Enable HDL file parsing
        :type parse_file: bool
        :param netlist_inst: Instantiation path of netlist
        :type netlist_inst: str
        :param code_coverage: Enable code coverage for this file
        :type code_coverage: bool
        """
        # Update library name if specified, othervise previous will be used
        if library_name:
            self.set_library(library_name)

        if hdl_version is None:
            hdl_version = "2008"
        elif isinstance(hdl_version, int):
            hdl_version = str(hdl_version)

        # Get library object to store file objects
        library = self._get_library_object(self.settings.get_library_name())
        library.add_file(
            filename=filename,
            hdl_version=hdl_version,
            com_options=com_options,
            parse_file=parse_file,
            code_coverage=code_coverage,
            netlist_instance=netlist_inst,
        )

    def add_file(
        self,
        filename: str,
        library_name: str = None,
        hdl_version: str = None,
        com_options: str = None,
        parse_file=True,
        netlist_inst: str = None,
        code_coverage: bool = False,
    ):
        """
        Overloading for add_files()
        """
        self.add_files(
            filename,
            library_name=library_name,
            hdl_version=hdl_version,
            com_options=com_options,
            parse_file=parse_file,
            netlist_inst=netlist_inst,
            code_coverage=code_coverage,
        )

    def add_file_to_run_folder(self, filename: str, tc_id: str):
        """
        Copies a file to the folder where a testcase is run from.

        :param: filename : filename with full or relative path
        :type filename : str
        :param: tc_id : testcase id number that use included file
        :type tc_id : str

        """
        self.testcase_settings.copy_file_to_testcase_folder(filename, tc_id)

    def remove_file(self, filename, library_name):
        """
        Remove a file that has been added to a library object

        :param library_name: Name of library to add file
        :type library_name: str

        :param filename; Name of file to be added to library
        :type filename: str
        """
        # Get library object to store file objects
        library = self._get_library_object(library_name)
        library.remove_file(filename)

    def set_dependency(self, library_name: str, dependent_libs: list):
        """
        Allows for manually define library dependency.

        :param library_name: Library that are added dependent libraries.
        :type library_name : str
        :param dependent_libs: Name of dependency libraries
        :type dependent_libs: list of str
        """
        lib = self._get_library_object(
            library_name=library_name, create_new_if_missing=False, precompiled=False
        )
        if lib:
            for dep_lib in dependent_libs:
                lib.add_lib_dep(dep_lib)
        else:
            self.logger.warning("Library %s not found." % (library_name))

    def set_library(self, library_name: str):
        """
        Sets the current working library.

        :param library_name: Name of default library
        :type library_name: str
        """
        self.settings.set_library_name(library_name.lower())

    def add_generics(
        self, entity: str, architecture: str = None, generics: list = None
    ):
        """
        Adds generic info to a Container Object generic_container.
        Accepts input in format: [<test_name>, <architecture>, [<generic_name>, <generic_value>]].

        :param entity: Testbench entity name to add generics
        :type entity: str
        :param  architecture: Name of architecture to run with testbench entity.
        :type architecture: str
        :param generics: Generic name and value pairs to construct testcase with.
        :type generics: list of str
        """
        # Adjust any path values
        generic_list = adjust_generic_value_paths(generics, self.settings, self.logger)

        if not len(generic_list) % 2 == 0:
            self.logger.warning(
                "Error in generic list. Usage: <test_name>, [<generic_name>, <generic_value>]"
            )
        else:
            generic_container_located = False
            # Check if generic container for the test exist
            for container in self.generic_container.get():
                if container.get_name().upper() == entity.upper():
                    generic_container_located = True
                    self.logger.debug(
                        "Adding %s to new generic container for %s."
                        % (generic_list, entity)
                    )
                    add_ok = container.add([architecture, generic_list])
                    if add_ok is False:
                        self.logger.warning(
                            "Duplicate generics: %s"
                            % ([entity, architecture, generic_list])
                        )

            if generic_container_located is False:
                # Create a new container when no generic container for the test was found
                self.logger.debug(
                    "Adding %s to new generic container for %s."
                    % (generic_list, entity)
                )
                container = Container(entity.upper())
                container.add([architecture, generic_list])
                self.generic_container.add(container)

    def gen_report(
        self,
        report_file: str = "report.txt",
        compile_order: bool = False,
        spec_cov: bool = False,
        library: bool = False,
    ):
        """
        Setup the reporting method.

        :param report_file: Name of file to write test run report
        :type report_file: str
        :param compile_order: Write the compile order if set to True
        :type compile_order: bool
        :param spec_cov: Write specification coverage if set to True
        :type spec_cov: bool
        :param library: Write library information if set
        :type library: bool
        """
        # Get the file extension in lower case
        file_extension = os.path.splitext(report_file)[1].lower()
        if report_file.lower().endswith(".txt"):
            self.reporter = TXTReporter(filename=report_file, project=self)
        elif report_file.lower().endswith(".csv"):
            self.reporter = CSVReporter(filename=report_file, project=self)
        elif report_file.lower().endswith(".json"):
            self.reporter = JSONReporter(filename=report_file, project=self)
        elif report_file.lower().endswith(".xml"):
            self.reporter = XMLReporter(filename=report_file, project=self)
        elif report_file.lower().endswith(".html") or report_file.lower().endswith(".htm"):
            self.reporter = HTMLReporter(filename=report_file, project=self)
        else:
            self.logger.warning(
                "Unsupported report file type: %s. Using: report_file.txt"
                % (file_extension)
            )
            self.reporter = TXTReporter(filename="report.txt", project=self)

        self.reporter.set_report_items(
            report_compile_order=compile_order,
            report_spec_cov=spec_cov,
            report_library=library,
        )

    def set_simulator(
        self,
        simulator: str,
        path: str = None,
        com_options: str = None,
        display_missing_simulator_path=True,
    ):
        """
        Sets the simulator in the project config.

        :param simulator: Name of simulator to use with simulations.
        :type simulator: str
        :param path: Absolute path to simulator.
        :type path: str
        :param com_options: Compile options to use with simulator.
        :type com_options: str
        """
        if not path and display_missing_simulator_path is True:
            self.logger.info(
                "Simulator {} expected to be in path environment.".format(simulator)
            )

        if not simulator:
            self.logger.warning("Missing argument: set_simulator(simulator=?).")
            return

        self.settings.set_simulator_name(simulator)
        self.settings.set_simulator_path(path)
        if com_options is not None:
            self.settings.set_com_options(com_options)

    def set_result_check_string(self, check_string: str):
        """
        Defines the simulation success creteria string.
        Default is UVVM summary report.

        :param check_string: String to use for detecting PASSed tests when
                             scanning simulation log file.
        :type check_string: str
        """
        self.settings.set_result_check_str(check_string)

    def add_testcase(self, testcase: str):
        """
        Configure to only run these testcases.
        Acceps testcase as string and list of strings.

        :param testcase: Name of testcase to run.
        :type testcase: str
        """
        if self.settings.get_cli_override() is False:
            if isinstance(testcase, list):
                for testcase_list_item in testcase:
                    self.settings.set_testcase(testcase_list_item)
            elif isinstance(testcase, str):
                self.settings.set_testcase(testcase)
            else:
                self.logger.warning(
                    "Unsupported type for add_testcase(): %s" % (type(testcase))
                )

    def add_to_testgroup(
        self,
        testgroup_name: str,
        entity: str,
        architecture: str = None,
        testcase: str = None,
        generic: list = None,
    ):
        """
        Adds one or more testbenches/testcases to a testgroup.
        The testgroup collection container holds testgroup containers, each
        with a testgroup_name and a list of testbenches/testcases.

        :param testgroup_name: Name of the test group that test is added.
        :type testgroup_name: str
        :param entity: Name of testbench entity to add
        :type entity: str
        :param architecture: Name of architecture to use with testbench entity.
        :type architecture: str
        :param testcase: Name of sequencer built-in testcase to run in architecture.
        :type testcase: str
        :param generic: List of generic name and value pairs to use with test
        :type generic: list of str
        """
        v_params_ok = validate_testgroup_parameters(
            testgroup_name, entity, architecture, testcase, generic
        )

        if v_params_ok is True:
            # Locate testgroup container
            testgroup_container = self._get_testgroup_container(testgroup_name)
            test_to_run = (entity, architecture, testcase, generic)
            testgroup_container.add(test_to_run)
            self.logger.debug(
                "Added %s to container %s."
                % (test_to_run, testgroup_container.get_name())
            )
        else:
            self.logger.warning(
                "add_to_testgroup(%s, %s, %s, %s, %s failed."
                % (testgroup_name, entity, architecture, testcase, generic)
            )

    def set_testcase_identifier_name(self, tc_id: str = "gc_testcase"):
        """
        Sets the generic value used for identifying testcases.
        Default is gc_testcase.

        :param tc_id: Name of sequencer built-in testcase generic
        :type tc_id: str
        """
        self.logger.debug("Setting testcase identifier to %s." % (tc_id))
        self.settings.set_testcase_identifier_name(tc_id.lower())

    def set_code_coverage(
        self,
        code_coverage_settings: str,
        code_coverage_file: str,
        exclude_file: str = None,
        merge_options: str = None,
    ):
        """
        Defines the code coverage for all tests

        :param code_coverage_settings: Coverage collection settings when running simulations.
        :type code_coverage_settings: str
        :param code_coverage_file: Name of generated coverage file (without path).
        :type code_coverage_file: str
        :param exclude_file: Name of file with coverage exceptions.
        :type exclude_file: str
        :param merge_options: Additional options to run in a vcov merge call.
        :type merge_options: str
        """
        self.hdlcodecoverage.set_code_coverage_settings(code_coverage_settings)
        self.hdlcodecoverage.set_code_coverage_file(code_coverage_file)
        self.hdlcodecoverage.set_exclude_file(exclude_file)
        self.hdlcodecoverage.set_options(merge_options)

    def set_simulator_wave_file_format(self, wave_format):
        """
        Set format for NVC or GHDL wave dump file.
        Options are 'VCD' and 'FST'.

        :param wave_format: Wave format
        :type wave_format: str
        """
        self.settings.set_simulator_wave_file_format(wave_format)

    def set_pre_sim_tcl_command(self, tcl_command):
        """
        Set TCL command which is to be run before the test is started.

        :param tcl_command: TCL command which is to be run before the test is started.
        """
        self.settings.simulator_settings.set_pre_sim_tcl_command(tcl_command)

    def start(self, **kwargs) -> int:
        """
        Run HDLRegression with the loaded settings.

        :param gui_mode: Enables simulation run in GUI
        :type gui_mode: bool
        :param stop_on_failure: Stops running new testcases if a testcase fails.
        :type stop_on_failure: bool
        :param regression_mode: run all testcases.
        :type regression_mode: bool
        :param threading: Enables running of tasks in parallel.
        :type threading: bool

        :rtype: int
        :return: Run result, 0=Pass, 1=Fail/No tests to run
        """
        kwargs = dict_keys_to_lower(kwargs)

        update_settings_from_arguments(project=self, kwargs=kwargs)

        self._prepare_libraries()

        self._setup_simulation_runner()

        self.hdlcodecoverage.get_code_coverage_obj(self.settings.get_simulator_name())

        self._remove_empty_libraries()

        # ========================================
        # Case on what to execute/do
        # ========================================

        # pylint: disable=protected-access
        if self.settings.get_list_testcase():
            print(list_testcases(self.runner))

        elif self.settings.get_export_testcases_json_path():
            print(export_testcases_to_json(self.runner,self.settings.get_export_testcases_json_path()))

        elif self.settings.get_list_dependencies():
            for library in self.library_container.get():
                print(library._present_library())

        elif self.settings.get_list_compile_order():
            print(list_compile_order(self.library_container))

        elif self.settings.get_list_testgroup():
            print(list_testgroup(self.testgroup_collection_container))

        # pylint: enable=protected-access
        elif run_from_gui(project=self) is True:
            """
            HDLRegression is started with argument "-g" for GUI and will
            create a tcl file and start Modelsim with this file.
            No tests are run in this mode, but testcases are manually started
            from Modelsim GUI using the "s" command (simulate).
            """
            self.logger.info("Simulator: {}".format(self.runner.get_simulator_name()))

            if self.settings.get_simulator_name() == "MODELSIM":
                self.runner = TclRunnerModelsim(project=self)
            elif self.settings.get_simulator_name() == "RIVIERA-PRO":
                self.runner = TclRunnerRiviera(project=self)
            elif self.settings.get_simulator_name() == "ACTIVE-HDL":
                self.runner = TclRunnerActiveHDL(project=self)

            # Prepare modelsim.ini file
            modelsim_ini_file = self.runner._setup_ini()
            self._add_precompiled_libraries_to_modelsim_ini(modelsim_ini_file)

            self.runner.prepare_test_modules_and_objects(self.re_run_tc_list)
            (compile_success, self.library_container) = self.runner.compile_libraries()

            if not compile_success:
                self.settings.set_return_code(1)
                self.logger.info("Compilation failed - aborting!")
            else:
                # Need to save project settings for Tcl Runner to know about
                # libraries and files set in the regression script.
                self._save_project_to_disk(reset=False)

                # create tcl file and start GUI mode.
                self.runner.simulate_gui()

                print_info_msg_when_no_test_has_run(project=self, runner=self.runner)

                # restore settings gui mode
                self.settings.set_gui_mode(HDLRegressionSettings().get_gui_mode())

                # Save any settings that have been made while running TCL Runner.
                self._save_project_to_disk(reset=True)

        else:
            """
            HDLRegression is called without run arguments, or the "-fr" argument.
            Only tests affected by changes are run, unless the "-fr" argument,
            or no previous test runs have been made, then all tests are run.
            """
            self.logger.info("Simulator: {}".format(self.runner.get_simulator_name()))
            self._validate_simulator_with_cached(self.runner.get_simulator_name())

            # Prepare modelsim.ini file
            modelsim_ini_file = self.runner._setup_ini()
            self._add_precompiled_libraries_to_modelsim_ini(modelsim_ini_file)

            self.runner.prepare_test_modules_and_objects(self.re_run_tc_list)

            # Compile libraries and files
            (compile_success, self.library_container) = self.runner.compile_libraries()

            # Update return_code if compilation has failed
            if compile_success is False:
                self.settings.set_return_code(1)

            # Start simulations if compile was OK
            else:
                if self.settings.get_no_sim() is True:
                    self.logger.info("\nSkipping simulations")
                    self.runner.mark_tests_for_re_run()

                else:
                    self.logger.info("\nStarting simulations...")
                    sim_success = self.runner.simulate() if self.runner else False

                    if not sim_success or (self.get_num_fail_tests() > 0):
                        self.settings.set_return_code(1)
                    else:
                        # Single testcase run is not a valid regression
                        if self.settings.get_testcase() is None:
                            self.settings.set_run_success(True)
                            self.settings.set_time_of_run()

                        print_info_msg_when_no_test_has_run(
                            project=self, runner=self.runner
                        )

                # Do not save running a selected testcase
                self.settings.empty_testcase_list()

                # Disable threading
                disable_threading(project=self)

                # Save settings befor returning to project script.
                self._save_project_to_disk(reset=True)

        if self.get_num_tests_run() > 0:
            print_run_success(project=self)
            self._generate_run_report_files()
        else:
            if self.settings.get_no_sim() is False:
                self.settings.set_return_code(1)

        # Merge coverage files and generate reports.
        if self.hdlcodecoverage.merge_code_coverage() is False:
            self.logger.warning("Code coverage report failed.")

        # Exit regression with return code
        return self.settings.get_return_code()

    def get_results(self) -> list:
        """
        Returns a list of lists with passed, failed, and not run tests.

        :rtype: list
        :return: List of all tests in run.
        """
        if self.runner:
            return self.runner.get_test_result()
        else:
            return [[], [], []]

    def get_num_tests_run(self) -> int:
        """
        Returns the number of tests that have been run.

        :rtype: int
        :return: Number of run tests.
        """
        return self.runner.get_num_tests_run()

    def get_num_pass_tests(self) -> int:
        """
        Returns the number of tests that have passed in this run.

        :rtype: int
        :return: Number of passing tests in run.
        """
        return self.runner.get_num_pass_test()

    def get_num_fail_tests(self) -> int:
        """
        Returns the number of tests that have failed in this run.

        :rtype: int
        :return: Number of failing tests in run.
        """
        return self.runner.get_num_fail_test()

    def get_num_pass_with_minor_alert_tests(self) -> int:
        """
        Returns the number of tests that have passed in this run, but
        also has one or more minor alerts.

        :rtype: int
        :return: number of passed tests in run.
        """
        return self.runner.get_num_pass_with_minor_alerts_test()

    def check_run_results(
        self, exp_pass: int = None, exp_fail: int = None, exp_run: int = None
    ) -> bool:
        """
        Compares the expected outcome of a test run with actual.

        :param exp_pass: number of expected tests to have passed.
        :type exp_pass: int
        :param exp_fail: number of expected tests to have failed.
        :type exp_fail: int
        :param exp_run: number of expected tests to have been run.
        :type exp_run: int

        :rtype: bool
        :return: True if expected result matches actual.
        """
        actual_pass = self.get_num_pass_tests()
        actual_fail = self.get_num_fail_tests()
        actual_run = self.get_num_tests_run()
        check_ok = True

        if exp_pass is not None:
            if exp_pass != actual_pass:
                self.logger.error(
                    "%sNumber of pass test mismatch: "
                    "exp=%d, actual=%d.%s"
                    % (
                        self.logger.red(),
                        exp_pass,
                        actual_pass,
                        self.logger.reset_color(),
                    )
                )
                check_ok = False
            else:
                self.logger.info(
                    "%sNumber of pass tests OK.%s"
                    % (self.logger.green(), self.logger.reset_color())
                )

        if exp_fail is not None:
            if exp_fail != actual_fail:
                self.logger.error(
                    "%sNumber of fail test mismatch: "
                    "exp=%d, actual=%d.%s"
                    % (
                        self.logger.red(),
                        exp_fail,
                        actual_fail,
                        self.logger.reset_color(),
                    )
                )
                check_ok = False
            else:
                self.logger.info(
                    "%sNumber of fail tests OK.%s"
                    % (self.logger.green(), self.logger.reset_color())
                )

        if exp_run is not None:
            if exp_run != actual_run:
                self.logger.error(
                    "%sNumber of test run mismatch: "
                    "exp=%d, actual=%d.%s"
                    % (
                        self.logger.red(),
                        exp_run,
                        actual_run,
                        self.logger.reset_color(),
                    )
                )
                check_ok = False
            else:
                self.logger.info(
                    "%sNumber of test run OK.%s"
                    % (self.logger.green(), self.logger.reset_color())
                )

        return check_ok

    def run_command(self, command: str, verbose: bool = False) -> tuple:
        """
        Runs command in terminal and returns the exit code, i.e.
        0 for success and 1 for failure.

        :param command: the command to execute
        :type command: str/list
        :param verbose: terminal output verbosity setting
        :type verbose: bool

        :rtype: (str, int)
        :return: (output, return_code), Command execution output,
                                        Command execution return code.
        """

        # convert to list
        if isinstance(command, str):
            command = command.split(" ")
        if not isinstance(command, list):
            self.logger.error(
                "run_command() parameter should be list or string, not %s."
                % (type(command))
            )
        else:
            self.logger.debug("run_command(): %s" % (command))
            (output, error_code) = CommandRunner(project=self).script_run(
                command, verbose=verbose
            )
            return (output, error_code)

    def configure_library(
        self, library: str, never_recompile: bool = None, set_lib_dep: str = None
    ):
        """
        Method allows for special configurations for libraries.

        :param library: name of the library that are configured.
        :type library: str
        :param: never_recompile: disables recompilation of library.
        :type never_recompile: bool
        :param set_lib_dep: name of libray that are added to 'library' dependency list.
        :type set_lib_dep: str
        """
        # Locate or create new HDLLibrary object
        lib = self._get_library_object(library)
        # Add changes to library
        if never_recompile:
            lib.set_never_recompile(never_recompile)
        if set_lib_dep:
            lib.add_lib_dep(set_lib_dep)

    def compile_uvvm(self, path_to_uvvm: str) -> bool:
        """
        Compiles the entire UVVM verification library to
        HDLRegression compile libraries.

        :param path_to_uvvm: the path to where UVVM is located on HD.
        :type path_to_uvvm: str

        :rtype: bool
        :return: True when command is valid
        """

        return compile_uvvm_all(project=self, path=path_to_uvvm)

    def compile_osvvm(self, path_to_osvvm: str) -> bool:
        """
        Compiles the entire OSVVM verification library.

        :param path_to_osvvm: the path to where OSVVM is located on HD.
        :type path_to_osvvm: str

        :rtype: bool
        :return: True when command is valid
        """
        return compile_osvvm_all(project=self, path=path_to_osvvm)

    def get_args(self):
        """
        Returns the parsed arguments from HDLRegression
        """
        return self.args

    def get_file_list(self) -> list:
        """
        Returns a list of all files in the project.
        """
        file_list = []
        for lib in self.library_container.get():
            for file in lib.get_hdlfile_list():
                file_list.append(file.get_filename_with_path())
        return file_list

    # pylint: enable=too-many-arguments

    # ========================================================
    #
    # Non-public methods
    #
    # ========================================================

    def _initialize_settings(self, arg_parser):
        self.settings_config = SettingsConfigurator(project=self)
        self.args = arg_parser_reader(arg_parser=arg_parser)
        return self.settings_config.setup_settings(HDLRegressionSettings(), self.args)

    def _initialize_logger(self):
        return Logger(__name__, project=self)

    def _setup_logger(self) -> None:
        self.logger.set_level(self.settings.get_logger_level())

    def _initialize_hdl_code_coverage(self):
        return HdlCodeCoverage(project=self)

    def _initialize_signal_handler(self):
        signal(SIGINT, exit_handler)

    def _validate_simulator_with_cached(self, sim_name: str = None) -> None:
        if self.settings.get_clean():
            return

        if self.cached_simulator_settings is None:
            return
        cached_sim_name = self.cached_simulator_settings.get_simulator_name()
        sim_name = self.settings.get_simulator_name()

        if not cached_sim_name:
            return

        if cached_sim_name != sim_name.upper():
            self.logger.error(
                "HDLRegression cache was run using {} simulator, current simulator is {}. Aborting".format(
                    cached_sim_name, sim_name
                )
            )
            sys.exit(1)

    def _set_simulator(self, sim_name: str = None):
        if sim_name:
            self.settings.set_simulator_name(sim_name)
            self.hdlcodecoverage.get_code_coverage_obj(sim_name)

    def _load_project_data(self, output_path: str):
        self.hdlcodecoverage = HdlCodeCoverage(project=self)

        # Load HDLRegression install version number.
        installed_version = self._get_install_version()
        display_info_text(version=installed_version)

        self.detected_simulators = simulator_detector()

        # # Load any previously saved HDLRegression cache.
        self._load_project_databases(output_path)

        # Validate cached HDLRegression version, i.e. saved DB.
        version_ok = validate_cached_version(
            project=self, installed_version=installed_version
        )
        self._rebuild_databases_if_required_or_requested(version_ok, output_path)

        # Update cached version (settings) with installed version number.
        self.settings.set_hdlregression_version(installed_version)

    def _rebuild_databases_if_required_or_requested(
        self, version_ok: bool, output_path: str
    ):
        """
        Execute deleting of DBs and building of new DBs.

        :param version_ok: Status of cached version vs install version check.
        :type version_ok: bool
        """
        if (version_ok is False) or (self.settings.get_clean()):
            empty_project_folder(project=self)
            self._load_project_databases(output_path)

    def _generate_run_report_files(self):
        if not self.reporter:
            self.gen_report()
        self.reporter.report()

    def _add_precompiled_libraries_to_modelsim_ini(self, modelsim_ini_file: str):
        if modelsim_ini_file is not None:
            # Create string with precompiled libraries
            lib_string = ""
            lib_to_remove = []
            for lib in self.library_container.get():
                if isinstance(lib, PrecompiledLibrary):
                    self.logger.info(
                        "Setting up precompiled library: %s" % (lib.get_name())
                    )
                    lib_string += "%s = %s\n" % (
                        lib.get_name(),
                        os.path.realpath(lib.get_compile_path()),
                    )
                    lib_to_remove.append(lib)

            # Remove precompiled libraries
            for lib in lib_to_remove:
                self.library_container.remove(lib.get_name())

            # Write to modelsim.ini
            if lib_string:
                with open(modelsim_ini_file, mode="r") as read_file:
                    read_lines = read_file.readlines()

                write_lines = ""
                for read_line in read_lines:
                    write_lines += read_line.replace(
                        "[Library]", "[Library]\n%s" % (lib_string)
                    )

                with open(modelsim_ini_file, mode="w") as f:
                    f.writelines(write_lines)

    def _prepare_libraries(self) -> None:
        """
        Runs a series of library commands to prepare libraries and
        their files for dependency detection, compilation and
        simulations.
        """
        # Make all Library objects prepare for compile/simulate
        self.logger.info("Scanning files...")
        request_libraries_prepare(project=self)
        # Organize the libraries by dependecy
        self.logger.info("Building test suite structure...")
        organize_libraries_by_dependency(project=self)

    def _setup_simulation_runner(self):
        # Get runner object based on configuration settings
        simulator = self.settings.get_simulator_name()
        self.runner = self._get_runner_object(simulator=simulator)

    def _start_gui(self) -> int:
        """
        HDLRegression is called from Modelsim GUI, i.e. to compile changes or
        every library and files. No tests are run in this mode.
        Compilation is started with the "r" and "rr" commands from
        Modelsim GUI.

        :rtype: int
        :return: The success of preparing for GUI run,
                 i.e. 0 for success and 1 for failure.
        """

        # return code default set to success
        # return_code = 0
        self.settings.set_return_code(0)

        # Get runner object based on configuration settings
        self.runner = self._get_runner_object(
            simulator=self.settings.get_simulator_name()
        )

        # Save this setting before reloading "initial" settings
        gui_compile_all = self.settings.get_gui_compile_all()

        # Update settings to GUI settings
        self.settings.set_verbose(True)
        self.settings.set_gui_compile_all(gui_compile_all)

        # Make all Library objects prepare for compile/simulate
        request_libraries_prepare(project=self)
        # Organize the libraries by dependecy
        organize_libraries_by_dependency(project=self)

        # Prepare modelsim.ini file
        modelsim_ini_file = self.runner._setup_ini()
        self._add_precompiled_libraries_to_modelsim_ini(modelsim_ini_file)

        # Compile libraries and files using the modelsim_runner
        (success, self.library_container) = self.runner.compile_libraries()

        if not success:
            # return_code = 1
            self.settings.set_return_code(1)
            print("hdlregression:failed")
        else:
            self.settings.set_run_success(True)
            self.settings.set_time_of_run()
            print("hdlregression:success")

        # Save settings befor returning to project script.
        self._save_project_to_disk(reset=True)

        # Exit with return code
        return self.settings.get_return_code()

    def _get_install_version(self) -> str:
        """
        :rtype: str
        :return: The HDLRegression install version number
                 as set in __init__.py'.
        """
        try:
            return __version__
        except:
            self.logger.warning("Unable to read version number.")
        return "0.0.0"

    def _get_install_path(self) -> str:
        """
        Returns the HDLRegression installation path as a string.

        :rtype: str
        :return: HDLRegression installation path on system.
        """
        install_path = os.path.join(src_path, "..")
        return os_adjust_path(install_path)

    def _get_runner_object(self, simulator: str) -> "Runner":
        """
        Creates and returns a HDLRunner Object for running simulations.

        :param simulator: Name of simulator to run tests.
        :type simulator: str

        :rtype: Runner
        :return: Simulator runner object.
        """
        if simulator == "MODELSIM":
            runner_obj = ModelsimRunner(project=self)
        elif simulator == "RIVIERA-PRO":
            runner_obj = RivieraRunner(project=self)
        elif simulator == "ACTIVE-HDL":
            runner_obj = ActiveHDLRunner(project=self)
        elif simulator == "GHDL":
            runner_obj = GHDLRunner(project=self)
        elif simulator == "NVC":
            runner_obj = NVCRunner(project=self)
        elif simulator == "VIVADO":
            runner_obj = VivadoRunner(project=self)
        else:
            sim_info = self.settings.get_simulators_info()
            sim_name = sim_info.get("simulator")
            self.logger.warning(
                "Simulator %s not available. Autodetecting: %s" % (simulator, sim_name)
            )
            self._set_simulator(sim_name)
            runner_obj = self._get_runner_object(sim_name)
        return runner_obj

    def _load_project_databases(self, output_path: str) -> None:
        # Load previous run if available, or create new containers
        self._load_project_from_disk(output_path)

        # Create basic output folders if they do not exist
        try:
            if not os.path.exists(self.settings.get_output_path()):
                os.mkdir(self.settings.get_output_path())
            if not os.path.exists(self.settings.get_library_path()):
                os.mkdir(self.settings.get_library_path())
            if not os.path.exists(self.settings.get_test_path()):
                os.mkdir(self.settings.get_test_path())
        except OSError as error:
            self.logger.error("Unable to create project folder: %s" % (error))

        # Adjust settings with terminal arguments as these
        # might have been overwritten by _load_project_from_disk().
        self.settings = self.settings_config.setup_settings(self.settings, self.args)
        # Set path for hdlregression install (src) and simulation folder
        self.settings.set_src_path(src_path)  # HDLRegression install path
        # Path where regression script is called from, i.e. "/sim"
        self.settings.set_sim_path(sim_path)
        # Path of regression script, i.e. "/script"
        self.settings.set_script_path(script_path)
        self.settings.set_return_code(0)

    # ====================================================================
    # Container methods
    # ====================================================================

    def _remove_empty_libraries(self):
        for lib in self.library_container.get():
            if len(lib.get_hdlfile_list()) == 0 and lib.get_is_precompiled() is False:
                self.library_container.remove(lib)

    def _get_library_container(self) -> "Container":
        """
        :rtype: Container
        :return: Container with defined libraries.
        """
        return self.library_container

    def _get_testgroup_container(
        self, testgroup_name: str, create_if_not_found: bool = True
    ) -> "Container":
        """
        Locate the testgroup container, or get a new if not found.

        :param testgroup_name: Name of testgroup container to get/create
        :type testgroup_name: str
        :param create_if_not_found: Selects if a missing container should be created.
        :type create_if_not_found: bool

        :rtype: Container
        :return: Testgroup container
        """
        for testgroup_container in self.testgroup_collection_container.get():
            # Testgroup container located
            if testgroup_container.get_name() == testgroup_name.lower():
                return testgroup_container

        if create_if_not_found is True:
            new_container = Container(testgroup_name)
            self.testgroup_collection_container.add(new_container)
            return new_container
        # else
        return None

    # ====================================================================
    # Library methods
    # ====================================================================

    def _get_library_object(
        self,
        library_name: str,
        create_new_if_missing: bool = True,
        precompiled: bool = False,
    ) -> "Library":
        """
        Check if a library object has been created and returns it,
        creates a new and returns it if no library match was found.

        :param library_name: Library object name
        :type library_name: str
        :param create_new_if_missing: Selects if missing library object should be created.
        :type create_new_if_missing: bool
        :param precompiled: Flags library object as a precompiled library
        :type precompiled: bool

        :rtype: Library
        :return: An existing or new library object
        """
        # Check all libraries stored in structure
        for lib_obj in self.library_container.get():
            # Found a match, return it
            if lib_obj.get_name() == library_name:
                return lib_obj

        if create_new_if_missing is True:
            # No match was found, creating a new and returning it
            self.logger.debug("Creating library object: %s." % (library_name))
            if precompiled is False:
                lib_obj = HDLLibrary(name=library_name, project=self)
            else:
                lib_obj = PrecompiledLibrary(name=library_name, project=self)
            self.library_container.add(lib_obj)
            return lib_obj
        # else
        return None

    def _save_project_to_disk(self, reset: bool = True):
        """
        Save project structure to files.

        :param reset: Enables resetting of all HDLRegressionSettings obj settings.
        :type reset: bool
        """

        # Helper method
        def _dump(container, filename, output_path):
            filename = os.path.join(os.getcwd(), output_path, filename)
            filename = os_adjust_path(filename)
            dump_file = open(filename, "wb")
            pickle.dump(container, dump_file, pickle.HIGHEST_PROTOCOL)
            dump_file.close()

        settings_copy = copy.deepcopy(self.settings)
        simulator_settings = settings_copy.get_simulator_settings()
        if reset:
            # Do not save argument settings, i.e. this will make next run
            # behave as selected with previous run arguments.
            settings_copy = self.settings_config.unset_argument_settings(settings_copy)

        _dump(self.library_container, "library.dat", settings_copy.get_output_path())
        _dump(self.generic_container, "generic.dat", settings_copy.get_output_path())
        _dump(
            self.testgroup_container, "testgroup.dat", settings_copy.get_output_path()
        )
        _dump(
            self.testgroup_collection_container,
            "testgroup_collection.dat",
            settings_copy.get_output_path(),
        )
        _dump(settings_copy, "settings.dat", settings_copy.get_output_path())
        _dump(
            self.runner.get_re_run_test_obj_list(),
            "testcase.dat",
            settings_copy.get_output_path(),
        )
        _dump(simulator_settings, "simulator.dat", settings_copy.get_output_path())

    def _load_project_from_disk(self, output_path: str) -> None:
        """
        Load project structure from files.
        """

        # Helper method
        def _load(container, filename, output_path):
            filename = os.path.join(os.getcwd(), output_path, filename)
            filename = os_adjust_path(filename)
            try:
                load_file = open(filename, "rb")
                container = pickle.load(load_file)
                load_file.close()
            except:
                self.logger.debug("Unable to locate container file %s" % (filename))
            return container

        self.settings = _load(HDLRegressionSettings(), "settings.dat", output_path)
        self.settings.set_output_path(output_path)
        self.library_container = _load(Container("library"), "library.dat", output_path)

        self.generic_container = _load(Container("generic"), "generic.dat", output_path)
        self.testgroup_container = _load(
            Container("testgroup"), "testgroup.dat", output_path
        )
        self.testgroup_collection_container = _load(
            Container("testgroup_collection"), "testgroup_collection.dat", output_path
        )

        # self.failing_tc_list = _load([], "testcase.dat")
        self.re_run_tc_list = _load([], "testcase.dat", output_path)

        self.cached_simulator_settings = _load(
            self.cached_simulator_settings, "simulator.dat", output_path
        )

        # Do not load configured generics, testcases or testcase groups when
        # called from runner script, only from GUI
        if self.init_from_gui is False:
            self.generic_container.empty_list()
            self.testgroup_container.empty_list()
            self.testgroup_collection_container.empty_list()

        # default settings for success run and return code:
        self.settings.set_return_code(0)
        self.settings.set_run_success(True)


# pylint: disable=unused-argument


def exit_handler(signal_received, frame):
    """Gracefully exit HDLRegression when CTRL-C is pressed."""
    print("\nHDLRegression run aborted - exiting.")
    print(
        """
Note! Aborting HDLRegression can create errors in the run structure, thus
the next run should include the "-c" clean argument."""
    )
    os._exit(0)
