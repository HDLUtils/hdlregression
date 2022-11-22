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

import sys
import os
import shutil
import pickle
import inspect
import argparse
from multiprocessing.pool import ThreadPool
from signal import signal, SIGINT

# Enable terminal colors on windows OS∫
if os.name == 'nt':
    from ctypes import windll
    k = windll.kernel32
    k.SetConsoleMode(k.GetStdHandle(-11), 7)
    os.system('color')

# Path from where regression script is called
sim_path = os.getcwd()
# HDLRegression installation path
src_path = os.path.dirname(os.path.abspath(__file__))
# Regression script path
script_path = os.path.abspath(sys.path[0])

from .configurator import SettingsConfigurator
from .construct.hdllibrary import HDLLibrary, PrecompiledLibrary
from .run.runner_aldec import AldecRunner
from .run.runner_ghdl import GHDLRunner
from .run.runner_nvc import NVCRunner
from .run.runner_modelsim import ModelsimRunner
from .run.cmd_runner import CommandRunner
from .run.tcl_runner import TclRunner
from .report.txtreporter import TXTReporter
from .report.csvreporter import CSVReporter
from .report.jsonreporter import JSONReporter
from .construct.container import Container
from .settings import HDLRegressionSettings
from .report.logger import Logger
from .hdlregression_pkg import *
from .arg_parser import arg_parser_reader, get_parser
from .hdlcodecoverage import *


class HDLRegression:
    '''
    HDLRegression is a HDL regression testing tool for automating,
    and speeding up HDL simulations.

    The regression tool is especially greate for simulating
    testcases developed using UVVM, but UVVM is not required
    to run the regression tool.
    '''

    # pylint: disable=consider-using-f-string
    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-public-methods

    def __init__(self,
                 simulator: str=None,
                 init_from_gui: bool=False,
                 arg_parser=None):
        '''
        Initializes the HDLRegression class which provides a set
        of API methods for controlling the regression flow.

        :param simulator: Simulator to use for regression run
        :type simulator: str
        :param init_from_gui: Regression initialized in from GUI tcl call.
        :type init_from_gui: bool
        '''

        # Initialized from regression script, i.e. not from GUI
        self.init_from_gui = init_from_gui

        # Gracefully exit on CTRL-C
        signal(SIGINT, exit_handler)

        # Init configuration obj
        self.settings_config = SettingsConfigurator(project=self)
        
        # Create settings object
        self.settings = HDLRegressionSettings()

        self.args = arg_parser_reader(arg_parser=arg_parser)

        self.logger = Logger(__name__, project=self)
        self.hdlcodecoverage = HdlCodeCoverage(project=self)
        
        # Load HDLRegression install version number.
        installed_version = self._get_install_version()
        self._display_info_text(version=installed_version)

        # Adjust settings with terminal arguments
        self.settings = self.settings_config.setup_settings(self.settings,
                                                            self.args)

        self.detected_simulators = simulator_detector()

        # # Load any previously saved HDLRegression cache.
        self._load_project_databases()

        # Validate cached HDLRegression version, i.e. saved DB.
        version_ok = self._validate_cached_version(
            installed_version=installed_version)
        self._rebuild_databases_if_required_or_requested(version_ok)

        # Update cached version (settings) with installed version number.
        self.settings.set_hdlregression_version(installed_version)

        # Set simulator - will be overrided by CLI argument.
        if simulator:
            if not self.settings.get_simulator_is_cli_selected():
                self.set_simulator(simulator)
                self.hdlcodecoverage.get_code_coverage_obj(simulator)
            else:
                self.hdlcodecoverage.get_code_coverage_obj(self.settings.get_simulator_name())
        else:
            self.hdlcodecoverage.get_code_coverage_obj()

        # Reporter object
        self.reporter = None
        # Setup logger level
        self.logger.set_level(self.settings.get_logger_level())

    def add_precompiled_library(self,
                                compile_path: str,
                                library_name: str):
        '''
        Adds a precompiled library to the structure.
        Precompiled library file reference is added to Modelsim.ini

        :param compile_path: Path pointing to the precompiled library.
        :type compile_path: str
        :param library_name: Name of a precompiled library that is not to
                             be parsed.
        :type library_name: str
        '''
        lib = self._get_library_object(
            library_name=library_name, precompiled=True)
        lib.set_compile_path(compile_path)

    def add_files(self,
                  filename: str,
                  library_name: str=None,
                  hdl_version: str=None,
                  com_options: str=None,
                  parse_file=True,
                  netlist_inst: str=None,
                  code_coverage: bool=False):
        '''
        Add files to HDLRegression file list:
        1. Get a new or existing library object
        2. Pass filename to library object which will create file objects.

        :param filename; Name of file to be added to library
        :type filename: str
        :param library: Name of library to add file
        :type librart: str
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
        '''
        # Update library name if specified, othervise previous will be used
        if library_name:
            self.set_library(library_name)

        if hdl_version is None:
            hdl_version = "2008"
        elif isinstance(hdl_version, int):
            hdl_version = str(hdl_version)

        # Get library object to store file objects
        library = self._get_library_object(self.settings.get_library_name())
        library.add_file(filename=filename,
                         hdl_version=hdl_version,
                         com_options=com_options,
                         parse_file=parse_file,
                         code_coverage=code_coverage,
                         netlist_instance=netlist_inst)

    def add_file(self,
                 filename: str,
                 library_name: str=None,
                 hdl_version: str=None,
                 com_options: str=None,
                 parse_file=True,
                 netlist_inst: str=None,
                 code_coverage: bool=False):
        '''
        Overloading for add_files()
        '''
        self.add_files(filename,
                       library_name=library_name,
                       hdl_version=hdl_version,
                       com_options=com_options,
                       parse_file=parse_file,
                       code_coverage=code_coverage)

    def set_dependency(self,
                       library_name: str,
                       dependent_libs: list):
        '''
        Allows for manually define library dependency.

        :param library_name: Library that are added dependent libraries.
        :type library_name : str
        :param dependent_libs: Name of dependency libraries
        :type dependent_libs: list of str
        '''
        lib = self._get_library_object(library_name=library_name,
                                       create_new_if_missing=False,
                                       precompiled=False)
        if lib:
            for dep_lib in dependent_libs:
                lib.add_lib_dep(dep_lib)
        else:
            self.logger.warning("Library %s not found." % (library_name))

    def set_library(self,
                    library_name: str):
        '''
        Sets the current working library.

        :param library_name: Name of default library
        :type library_name: str
        '''
        self.settings.set_library_name(library_name.lower())

    def add_generics(self,
                     entity: str,
                     architecture: str=None,
                     generics: list=None):
        '''
        Adds generic info to a Container Object generic_container.
        Accepts input in format: [<test_name>, <architecture>, [<generic_name>, <generic_value>]].

        :param entity: Testbench entity name to add generics
        :type entity: str
        :param  architecture: Name of architecture to run with testbench entity.
        :type architecture: str
        :param generics: Generic name and value pairs to construct testcase with.
        :type generics: list of str
        '''
        # Adjust any path values
        generic_list = adjust_generic_value_paths(generics,
                                                  self.settings,
                                                  self.logger)

        if not len(generic_list) % 2 == 0:
            self.logger.warning(
                "Error in generic list. Usage: <test_name>, [<generic_name>, <generic_value>]")
        else:
            generic_container_located = False
            # Check if generic container for the test exist
            for container in self.generic_container.get():
                if container.get_name().upper() == entity.upper():
                    generic_container_located = True
                    self.logger.debug(
                        'Adding %s to new generic container for %s.' % (generic_list, entity))
                    add_ok = container.add([architecture, generic_list])
                    if add_ok is False:
                        self.logger.warning('Duplicate generics: %s' % (
                            [entity, architecture, generic_list]))

            if generic_container_located is False:
                # Create a new container when no generic container for the test was found
                self.logger.debug(
                    'Adding %s to new generic container for %s.' % (generic_list, entity))
                container = Container(entity.upper())
                container.add([architecture, generic_list])
                self.generic_container.add(container)

    def gen_report(self,
                   report_file: str="report.txt",
                   compile_order: bool=False,
                   spec_cov: bool=False,
                   library: bool=False):
        '''
        Setup the reporting method.

        :param report_file: Name of file to write test run report
        :type report_file: str
        :param compile_order: Write the compile order if set to True
        :type compile_order: bool
        :param spec_cov: Write specification coverage if set to True
        :type spec_cov: bool
        :param library: Write library information if set
        :type library: bool
        '''
        # Get the file extension in lower case
        file_extension = os.path.splitext(report_file)[1].lower()
        if report_file.lower().endswith('.txt'):
            self.reporter = TXTReporter(filename=report_file, project=self)
        elif report_file.lower().endswith('.csv'):
            self.reporter = CSVReporter(filename=report_file, project=self)
        elif report_file.lower().endswith('.json'):
            self.reporter = JSONReporter(filename=report_file, project=self)
        else:
            self.logger.warning(
                "Unsupported report file type: %s. Using: report_file.txt" % (file_extension))
            self.reporter = TXTReporter(
                filename="report.txt", project=self)

        self.reporter.set_report_items(report_compile_order=compile_order,
                                       report_spec_cov=spec_cov,
                                       report_library=library)

    def set_simulator(self,
                      simulator: str=None,
                      path: str=None,
                      com_options: str=None):
        '''
        Sets the simulator in the project config.

        :param simulator: Name of simulator to use with simulations.
        :type simulator: str
        :param path: Absolute path to simulator.
        :type path: str
        :param com_options: Compile options to use with simulator.
        :type com_options: str
        '''
        self.logger.debug("Setting simulator: %s." % (simulator))

        if not path:
            self.logger.info(
                "Simulator %s expected to be in path environment." % (simulator))
        if not simulator:
            self.logger.warning(
                "No simulator selected, running with Mentor Modelsim.")
            simulator = "modelsim"

        if self.settings.get_simulator_name() != simulator.upper():
            self.logger.error(
                'Simulator change require new databases - delete '
                './hdlregression folder and rerun test suite.')
            self.settings.set_return_code(1)

        self.settings.set_simulator_name(simulator)
        self.settings.set_simulator_path(path)
        if com_options is not None:
            self.settings.set_com_options(com_options)

    def set_result_check_string(self,
                                check_string: str):
        '''
        Defines the simulation success creteria string.
        Default is UVVM summary report.

        :param check_string: String to use for detecting PASSed tests when
                             scanning simulation log file.
        :type check_string: str
        '''
        self.settings.set_result_check_str(check_string)

    def add_testcase(self,
                     testcase: str):
        '''
        Configure to only run these testcases.
        Acceps testcase as string and list of strings.

        :param testcase: Name of testcase to run.
        :type testcase: str
        '''
        if self.settings.get_cli_override() is False:
            if isinstance(testcase, list):
                for testcase_list_item in testcase:
                    self.settings.set_testcase(testcase_list_item)
            elif isinstance(testcase, str):
                self.settings.set_testcase(testcase)
            else:
                self.logger.warning(
                    'Unsupported type for add_testcase(): %s' % (type(testcase)))

    def add_to_testgroup(self,
                         testgroup_name: str,
                         entity: str,
                         architecture: str=None,
                         testcase: str=None,
                         generic: list=None):
        '''
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
        '''
        v_params_ok = self._validate_testgroup_parameters(testgroup_name,
                                                          entity,
                                                          architecture,
                                                          testcase,
                                                          generic)

        if v_params_ok is True:
            # Locate testgroup container
            testgroup_container = self._get_testgroup_container(testgroup_name)
            test_to_run = (entity, architecture, testcase, generic)
            testgroup_container.add(test_to_run)
            self.logger.debug('Added %s to container %s.' % 
                              (test_to_run, testgroup_container.get_name()))
        else:
            self.logger.warning('add_to_testgroup(%s, %s, %s, %s, %s failed.'
                                % (testgroup_name, entity, architecture, testcase, generic))

    def set_testcase_identifier_name(self,
                                     tc_id: str='gc_testcase'):
        '''
        Sets the generic value used for identifying testcases.
        Default is gc_testcase.

        :param tc_id: Name of sequencer built-in testcase generic
        :type tc_id: str
        '''
        self.logger.debug('Setting testcase identifier to %s.' % (tc_id))
        self.settings.set_testcase_identifier_name(tc_id.lower())

    def set_code_coverage(self,
                          code_coverage_settings: str,
                          code_coverage_file: str,
                          exclude_file: str=None,
                          merge_opions: str=None):
        '''
        Defines the code coverage for all tests

        :param code_coverage_settings: Coverage collection settings when running simulations.
        :type code_coverage_settings: str
        :param code_coverage_file: Name of generated coverage file (without path).
        :type code_coverage_file: str
        :param exclude_file: Name of file with coverage exceptions.
        :type exclude_file: str
        :param merge_options: Additional options to run in a vcov merge call.
        :type merge_options: str
        '''
        self.hdlcodecoverage.set_code_coverage_settings(code_coverage_settings)
        self.hdlcodecoverage.set_code_coverage_file(code_coverage_file)
        self.hdlcodecoverage.set_exclude_file(exclude_file)
        self.hdlcodecoverage.set_options(merge_opions)

    def start(self, **kwargs) -> int:
        '''
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
        :return: Run result, 0=Pass, 1=Fail
        '''
        kwargs = dict_keys_to_lower(kwargs)

        self._update_settings_from_arguments(kwargs)

        self._prepare_libraries()

        self._setup_simulation_runner()
        
        self.hdlcodecoverage.get_code_coverage_obj(self.settings.get_simulator_name())

        # ========================================
        # Case on what to execute/do
        # ========================================

        # pylint: disable=protected-access
        if self.settings.get_list_testcase():
            print(list_testcases(self.runner))

        elif self.settings.get_list_dependencies():
            for library in self.library_container.get():
                print(library._present_library())

        elif self.settings.get_list_compile_order():
            print(list_compile_order(self.library_container))

        elif self.settings.get_list_testgroup():
            print(list_testgroup(self.testgroup_collection_container))

        # pylint: enable=protected-access
        elif self._run_from_gui() is True:
            '''
            HDLRegression is started with argument "-g" for GUI and will
            create a tcl file and start Modelsim with this file.
            No tests are run in this mode, but testcases are manually started
            from Modelsim GUI using the "s" command (simulate).
            '''
            self.runner = TclRunner(project=self)

            # Prepare modelsim.ini file
            modelsim_ini_file = self.runner._setup_ini()
            self._add_precompiled_libraries_to_modelsim_ini(modelsim_ini_file)

            self.runner.prepare_test_modules_and_objects()
            (compile_success, self.library_container) = self.runner.compile_libraries()

            if not compile_success:
                self.settings.set_return_code(1)
                self.settings.set_success_run(False)
                self.logger.info('Compilation failed - aborting!')
            else:
                self.settings.set_success_run(True)

                # Need to save project settings for Tcl Runner to know about
                # libraries and files set in the regression script.
                self._save_project_to_disk(lib_cont=self.library_container,
                                           generic_cont=self.generic_container,
                                           tg_cont=self.testgroup_container,
                                           tg_col_cont=self.testgroup_collection_container,
                                           settings=self.settings,
                                           reset=False)

                # create tcl file and start GUI mode.
                self.runner.simulate()

                # restore settings gui mode
                self.settings.set_gui_mode(
                    HDLRegressionSettings().get_gui_mode())
                # Save any settings that have been made while running TCL Runner.
                self._save_project_to_disk(lib_cont=self.library_container,
                                           generic_cont=self.generic_container,
                                           tg_cont=self.testgroup_container,
                                           tg_col_cont=self.testgroup_collection_container,
                                           settings=self.settings,
                                           reset=True)

        else:
            '''
            HDLRegression is called without run arguments, or the "-fr" argument.
            Only tests affected by changes are run, unless the "-fr" argument,
            or no previous test runs have been made, then all tests are run.
            '''
            # Prepare modelsim.ini file
            modelsim_ini_file = self.runner._setup_ini()
            self._add_precompiled_libraries_to_modelsim_ini(modelsim_ini_file)

            self.runner.prepare_test_modules_and_objects()

            # Compile libraries and files
            (compile_success, self.library_container) = self.runner.compile_libraries()

            # Update return_code if compilation has failed
            if compile_success is False:
                self.settings.set_return_code(1)
                self.settings.set_success_run(False)

            # Start simulations if compile was OK
            else:
                self.logger.info('\nStarting simulations...')
                # Run simulation
                sim_success = self.runner.simulate() if self.runner else False

                if not sim_success or (self.get_num_fail_tests() > 0):
                    self.settings.set_return_code(1)
                    self.settings.set_success_run(False)
                else:

                    # Single testcase run is not a valid regression
                    if self.settings.get_testcase() is None:
                        self.settings.set_success_run(True)
                        self.settings.set_time_of_run()

                    self._print_info_msg_when_no_test_has_run()

                # Do not save running a selected testcase
                self.settings.empty_testcase_list()

                # Disable threading
                self._disable_threading()

                # Save settings befor returning to project script.
                self._save_project_to_disk(lib_cont=self.library_container,
                                           generic_cont=self.generic_container,
                                           tg_cont=self.testgroup_container,
                                           tg_col_cont=self.testgroup_collection_container,
                                           settings=self.settings)

        if self.get_num_tests_run() > 0:
            self._print_run_success()
            self._generate_run_report_files()

        # Merge coverage files and generate reports.
        if self.hdlcodecoverage.merge_code_coverage() is False:
            self.logger.warning('Code coverage report failed.')

        # Exit regression with return code
        return self.settings.get_return_code()

    def get_results(self) -> list:
        '''
        Returns a list of lists with passed, failed, and not run tests.

        :rtype: list
        :return: List of all tests in run.
        '''
        return self.runner.get_test_result()

    def get_num_tests_run(self) -> int:
        '''
        Returns the number of tests that have been run.

        :rtype: int
        :return: Number of run tests.
        '''
        return self.runner.get_num_tests_run()

    def get_num_pass_tests(self) -> int:
        '''
        Returns the number of tests that have passed in this run.

        :rtype: int
        :return: Number of passing tests in run.
        '''
        return self.runner.get_num_pass_test()

    def get_num_fail_tests(self) -> int:
        '''
        Returns the number of tests that have failed in this run.

        :rtype: int
        :return: Number of failing tests in run.
        '''
        return self.runner.get_num_fail_test()

    def get_num_pass_with_minor_alert_tests(self) -> int:
        '''
        Returns the number of tests that have passed in this run, but
        also has one or more minor alerts.

        :rtype: int
        :return: number of passed tests in run.
        '''
        return self.runner.get_num_pass_with_minor_alerts_test()

    def check_run_results(self,
                          exp_pass: int=None,
                          exp_fail: int=None,
                          exp_run: int=None) -> bool:
        '''
        Compares the expected outcome of a test run with actual.

        :param exp_pass: number of expected tests to have passed.
        :type exp_pass: int
        :param exp_fail: number of expected tests to have failed.
        :type exp_fail: int
        :param exp_run: number of expected tests to have been run.
        :type exp_run: int

        :rtype: bool
        :return: True if expected result matches actual.
        '''
        actual_pass = self.get_num_pass_tests()
        actual_fail = self.get_num_fail_tests()
        actual_run = self.get_num_tests_run()
        check_ok = True

        if exp_pass is not None:
            if exp_pass != actual_pass:
                self.logger.error('%sNumber of pass test mismatch: '
                                  'exp=%d, actual=%d.%s' % (self.logger.red(),
                                                            exp_pass,
                                                            actual_pass,
                                                            self.logger.reset_color()))
                check_ok = False
            else:
                self.logger.info('%sNumber of pass tests OK.%s' % (
                    self.logger.green(), self.logger.reset_color()))

        if exp_fail is not None:
            if exp_fail != actual_fail:
                self.logger.error('%sNumber of fail test mismatch: '
                                  'exp=%d, actual=%d.%s' % (self.logger.red(),
                                                            exp_fail,
                                                            actual_fail,
                                                            self.logger.reset_color()))
                check_ok = False
            else:
                self.logger.info('%sNumber of fail tests OK.%s' % (
                    self.logger.green(), self.logger.reset_color()))

        if exp_run is not None:
            if exp_run != actual_run:
                self.logger.error('%sNumber of test run mismatch: '
                                  'exp=%d, actual=%d.%s' % (self.logger.red(),
                                                            exp_run,
                                                            actual_run,
                                                            self.logger.reset_color()))
                check_ok = False
            else:
                self.logger.info('%sNumber of test run OK.%s' % (
                    self.logger.green(), self.logger.reset_color()))

        return check_ok

    def run_command(self,
                    command: str,
                    verbose: bool=False) -> tuple:
        '''
        Runs command in terminal and returns the exit code, i.e.
        0 for success and 1 for failure.

        :param command: the command to execute
        :type command: str/list
        :param verbose: terminal output verbosity setting
        :type verbose: bool

        :rtype: (str, int)
        :return: (output, return_code), Command execution output,
                                        Command execution return code.
        '''

        # convert to list
        if isinstance(command, str):
            command = command.split(" ")
        if not isinstance(command, list):
            self.logger.error(
                "run_command() parameter should be list or string, not %s." % (type(command)))
        else:
            (output, error_code) = CommandRunner(
                project=self).script_run(command, verbose=verbose)
            return (output, error_code)

    def configure_library(self,
                          library: str,
                          never_recompile: bool=None,
                          set_lib_dep: str=None):
        '''
        Method allows for special configurations for libraries.

        :param library: name of the library that are configured.
        :type library: str
        :param: never_recompile: disables recompilation of library.
        :type never_recompile: bool
        :param set_lib_dep: name of libray that are added to 'library' dependency list.
        :type set_lib_dep: str
        '''
        # Locate or create new HDLLibrary object
        lib = self._get_library_object(library)
        # Add changes to library
        if never_recompile:
            lib.set_never_recompile(never_recompile)
        if set_lib_dep:
            lib.add_lib_dep(set_lib_dep)

    def compile_uvvm(self,
                     path_to_uvvm: str) -> str:
        '''
        Compiles the entire UVVM verification library to
        HDLRegression compile libraries.

        :param path_to_uvvm: the path to where UVVM is located on HD.
        :type path_to_uvvm: str

        :rtype: str
        :return: The command executed for compiling UVVM
        '''
        if self.settings.get_simulator_name() in ["MODELSIM", "ALDEC"]:
            lib_compile_path = os.path.join(sim_path, 'hdlregression/library')
            uvvm_script_path = os.path.join(path_to_uvvm, 'script')
            uvvm_script_file = os.path.join(uvvm_script_path, 'compile_all.do')

            lib_compile_path = os_adjust_path(lib_compile_path)
            uvvm_script_path = os_adjust_path(uvvm_script_path)
            uvvm_script_file = os_adjust_path(uvvm_script_file)

            cmd_to_run = ['vsim', '-c', '-do', 'do %s %s %s; exit -f' % (uvvm_script_file,
                                                                         uvvm_script_path,
                                                                         lib_compile_path)]
            self.run_command(cmd_to_run)
            return ' '.join(cmd_to_run)
        else:
            self.logger.warning('Unsupported simulator')
            return None

    def get_args(self):
      return self.args

    # pylint: enable=too-many-arguments

    # ========================================================
    #
    # Non-public methods
    #
    # ========================================================

    def _run_from_gui(self) -> bool:
      if self.settings.get_gui_mode():
        return self.settings.get_simulator_name() == "MODELSIM"
      else:
        return False

    # pylint: disable=too-many-arguments
    def _validate_testgroup_parameters(self,
                                       testgroup_name: str,
                                       entity: str,
                                       architecture: str,
                                       testcase: str,
                                       generic: list) -> bool:
        '''
        :param testgroup_name: Name of testgroup
        :type testgroup_name: str
        :param entity: Name of testbench entity
        :type entity: str
        :param architecture: Name of testbench architecture
        :type architecture: str
        :param testcase: Test sequencer built-in testcase
        :type testcase: str
        :param generic: Testcase run-generics
        :type generic: list

        :rtype: bool
        :return: True if all validated OK, otherwise False.
        '''
        v_arguments_ok = True
        if not architecture:
            if testcase or generic:
                v_arguments_ok = False
        if not testcase:
            if generic:
                v_arguments_ok = False

        if generic:
            if not isinstance(generic, list):
                v_arguments_ok = False
        if not isinstance(testgroup_name, str):
            v_arguments_ok = False
        if not isinstance(entity, str):
            v_arguments_ok = False

        if architecture:
            if not isinstance(architecture, str):
                v_arguments_ok = False
        if testcase:
            if not isinstance(testcase, str):
                v_arguments_ok = False
        return v_arguments_ok

    # pylint: enable=too-many-arguments
    def _rebuild_databases_if_required_or_requested(self,
                                                    version_ok: bool):
        '''
        Execute deleting of DBs and building of new DBs.

        :param version_ok: Status of cached version vs install version check.
        :type version_ok: bool
        '''
        if (version_ok is False) or (self.settings.get_clean()):
            self._empty_project_folder()
            self._load_project_databases()

    def _validate_cached_version(self,
                                 installed_version: str) -> bool:
        '''
        Compare installed version with cache version.

        :rtype: bool
        :return: True if cached version matches installed version.
        '''
        # Load cached HDLRegression version number
        cached_version = self.settings.get_hdlregression_version()
        cached_version_ok = True
        # Compare current version with cached version
        if (cached_version != installed_version) and (cached_version != '0.0.0'):
            self.logger.warning('WARNING! HDLRegression v%s not compatible with cached v%s. '
                                'Executing database rebuild.' % 
                                (installed_version, cached_version))
            cached_version_ok = False
        return cached_version_ok

    def _generate_run_report_files(self):
        if not self.reporter:
            self.gen_report()
        self.reporter.report()

    def _update_settings_from_arguments(self,
                                        kwargs: dict):
        '''
        Adjust the run settings with scripted run arguments
        passed on with the start() call.

        :param kwargs: Keyword arguments
        :type kwargs: dict
        '''

        # Update if GUI mode is selected without overriding terminal argument
        if not self.settings.get_gui_mode():
            if 'gui_mode' in kwargs:
                self.settings.set_gui_mode(kwargs.get('gui_mode'))

        # Set what to do if a testcase fails.
        if not self.settings.get_stop_on_failure():
            if 'stop_on_failure' in kwargs:
                self.settings.set_stop_on_failure(
                    kwargs.get('stop_on_failure'))

        # Regression_mode: only run new and changed code
        if self.settings.get_run_all() is True:  # CLI argument
            self.settings.set_run_all(True)
        elif 'regression_mode' in kwargs:  # API argument
            self.settings.set_run_all(kwargs.get('regression_mode'))
        else:  # default
            self.settings.set_run_all(False)

        # Enable multi-threading
        if 'threading' in kwargs:
            self.logger.info('Threading active.')
            self.settings.set_threading(kwargs.get('threading'))
        # Verbosity
        if 'verbose' in kwargs:
            self.settings.set_verbose(True)
        # Simulation options
        if 'sim_options' in kwargs:
            self.settings.set_sim_options(kwargs.get('sim_options'))
        if 'netlist_timing' in kwargs:
            self.settings.set_netlist_timing(kwargs.get('netlist_timing'))

        # Coverage options
        if 'keep_code_coverage' in kwargs:
            if kwargs.get('keep_code_coverage') is True:
                self.settings.set_keep_code_coverage(keep_code_coverage=True)

        # UVVM specific
        if 'no_default_com_options' in kwargs:
            if kwargs.get('no_default_com_options') is True:
                # Check if running with defaults
                if self.settings.get_is_default_com_options() is True:
                    self.settings.remove_com_options()

        if 'ignore_simulator_exit_codes' in kwargs:
            exit_codes = kwargs.get('ignore_simulator_exit_codes')
            if isinstance(exit_codes, list) is False:
                self.logger.warning('ignore_simulator_exit_codes is not list.')
            else:
                self.settings.set_ignored_simulator_exit_codes(exit_codes)

    def _clean_generated_output(self, restore_settings=False):
        saved_settings = self.settings
        self.settings.set_clean(True)
        self._rebuild_databases_if_required_or_requested(False)
        if restore_settings is True:
            self.settings = saved_settings

    def _print_info_msg_when_no_test_has_run(self):
        ''' Display info message if no tests have been run. '''
        if self.runner.get_num_tests() == 0:
            self.logger.info('\nNo tests found.')
            self.logger.info(
                'Ensure that the "--hdlregression:tb" (VHDL) / "//hdlregression:tb"'
                ' (Verilog) pragma is set in the testbench file(s).')
        elif self.get_num_tests_run() == 0:
            self.logger.info(
                'Test run not required. Use "-fr"/"--fullRegression" to re-run all tests.')

    def _disable_threading(self):
        ''' Disable threading so the next run will start as normal. '''
        self.settings.set_threading(False)
        self.settings.set_num_threads(1)

    def _print_run_success(self):
        if self.settings.get_return_code() == 0:
            self.logger.info('SIMULATION SUCCESS: %d passing test(s).'
                             % (self.get_num_pass_tests()), color='green')
            num_minor_alerts = self.get_num_pass_with_minor_alert_tests()
            if num_minor_alerts > 0:
                self.logger.warning(
                    '%d test(s) passed with minor alert(s).'
                    % (num_minor_alerts))
        else:
            self.logger.warning('SIMULATION FAIL: %d tests run, %d test(s) failed.'
                                % (self.get_num_tests_run(), self.get_num_fail_tests()))

    def _add_precompiled_libraries_to_modelsim_ini(self,
                                                   modelsim_ini_file: str):
        if modelsim_ini_file is not None:
            # Create string with precompiled libraries
            lib_string = ''
            lib_to_remove = []
            for lib in self.library_container.get():
                if isinstance(lib, PrecompiledLibrary):
                    self.logger.info(
                        'Setting up precompiled library: %s' % (lib.get_name()))
                    lib_string = '%s = %s\n' % (
                        lib.get_name(), lib.get_compile_path())
                    lib_to_remove.append(lib)

            # Remove precompiled libraries
            for lib in lib_to_remove:
                self.library_container.remove(lib.get_name())

            # Write to modelsim.ini
            if lib_string:
                with open(modelsim_ini_file, mode='r') as read_file:
                    read_lines = read_file.readlines()

                write_lines = ''
                for read_line in read_lines:
                    write_lines += read_line.replace(
                        '[Library]', '[Library]\n%s' % (lib_string))

                with open(modelsim_ini_file, mode='w') as f:
                    f.writelines(write_lines)

    def _prepare_libraries(self) -> None:
        '''
        Runs a series of library commands to prepare libraries and
        their files for dependency detection, compilation and
        simulations.
        '''
        # Make all Library objects prepare for compile/simulate
        self.logger.info('Scanning files...')
        self._request_libraries_prepare()
        # Organize the libraries by dependecy
        self.logger.info('Building test suite structure...')
        self._organize_libraries_by_dependency()

    def _setup_simulation_runner(self):
        # Get runner object based on configuration settings
        self.runner = self._get_runner_object(
            simulator=self.settings.get_simulator_name())

    def _start_gui(self) -> int:
        '''
        HDLRegression is called from Modelsim GUI, i.e. to compile changes or
        every library and files. No tests are run in this mode.
        Compilation is started with the "r" and "rr" commands from
        Modelsim GUI.

        :rtype: int
        :return: The success of preparing for GUI run,
                 i.e. 0 for success and 1 for failure.
        '''

        # return code default set to success
        # return_code = 0
        self.settings.set_return_code(0)

        # Get runner object based on configuration settings
        self.runner = self._get_runner_object(
            simulator=self.settings.get_simulator_name())

        # Save this setting before reloading "initial" settings
        gui_compile_all = self.settings.get_gui_compile_all()

        # Update settings to GUI settings
        self.settings.set_verbose(True)
        self.settings.set_gui_compile_all(gui_compile_all)

        # Make all Library objects prepare for compile/simulate
        self._request_libraries_prepare()
        # Organize the libraries by dependecy
        self._organize_libraries_by_dependency()

        # Prepare modelsim.ini file
        modelsim_ini_file = self.runner._setup_ini()
        self._add_precompiled_libraries_to_modelsim_ini(modelsim_ini_file)

        # Compile libraries and files using the modelsim_runner
        (success, self.library_container) = self.runner.compile_libraries()

        if not success:
            # return_code = 1
            self.settings.set_return_code(1)
            self.settings.set_success_run(False)
            print("hdlregression:failed")
        else:
            self.settings.set_success_run(True)
            self.settings.set_time_of_run()
            print("hdlregression:success")

        # Save settings befor returning to project script.
        self._save_project_to_disk(lib_cont=self.library_container,
                                   generic_cont=self.generic_container,
                                   tg_cont=self.testgroup_container,
                                   tg_col_cont=self.testgroup_collection_container,
                                   settings=self.settings)

        # Exit with return code
        return self.settings.get_return_code()
        # return return_code

    def _get_install_version(self) -> str:
        '''
        :rtype: str
        :return: The HDLRegression install version number
                 as read from 'version.txt'.
        '''
        version = '0.0.0'
        path = os.path.join(src_path, '../version.txt')
        try:
            with open(path, 'r') as read_file:
                version = read_file.readlines()[0].strip()
        except:
            self.logger.warning('Unable to read version.txt')
        return version

    def _display_info_text(self, version) -> None:
        ''' Presents HDLRegression version number and QR info. '''
        print('''
%s
  HDLRegression version %s
  Please see /doc/hdlregression.pdf documentation for more information.
%s

''' % ('=' * 70, version, '=' * 70))

    def _get_install_path(self) -> str:
        '''
        Returns the HDLRegression installation path as a string.

        :rtype: str
        :return: HDLRegression installation path on system.
        '''
        install_path = os.path.join(src_path, '..')
        return os_adjust_path(install_path)

    def _get_runner_object(self,
                           simulator: str) -> 'Runner':
        '''
        Creates and returns a HDLRunner Object for running simulations.

        :param simulator: Name of simulator to run tests.
        :type simulator: str

        :rtype: Runner
        :return: Simulator runner object.
        '''
        runner_obj = ModelsimRunner(project=self)
        if simulator == 'MODELSIM':
            runner_obj = ModelsimRunner(project=self)
        elif simulator == 'ALDEC':
            runner_obj = AldecRunner(project=self)
        elif simulator == 'GHDL':
            runner_obj = GHDLRunner(project=self)
        elif simulator == 'NVC':
            runner_obj = NVCRunner(project=self)
        else:
            self.logger.warning(
                "Unknown simulator: %s, using Modelsim." % (simulator))
        return runner_obj

    def _empty_project_folder(self):
        # Clean output, i.e. delete all
        if os.path.isdir(self.settings.get_output_path()):
            shutil.rmtree(self.settings.get_output_path())
            self.logger.info('Project output path %s cleaned.' % 
                             (self.settings.get_output_path()))
            try:
                os.mkdir(self.settings.get_output_path())
            except OSError as error:
                self.logger.error(
                    'Unable to create output folder, %s.' % (error))
        else:
            self.logger.info('No output folder to delete: %s.' % 
                             (self.settings.get_output_path()))

    def _load_project_databases(self) -> None:
        # Load previous run if available, or create new containers
        (self.library_container,
         self.generic_container,
         self.testgroup_container,
         self.testgroup_collection_container,
         self.settings) = self._load_project_from_disk()

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
        self.settings = self.settings_config.setup_settings(self.settings,
                                                            self.args)
        # Set path for hdlregression install (src) and simulation folder
        self.settings.set_src_path(src_path)  # HDLRegression install path
        # Path where regression script is called from, i.e. "/sim"
        self.settings.set_sim_path(sim_path)
        # Path of regression script, i.e. "/script"
        self.settings.set_script_path(script_path)
        self.settings.set_return_code(0)

    def _request_libraries_prepare(self) -> None:
        ''' Invoke all Library Objects to prepare for compile/simulate. '''

        # Thread method
        def library_prepare(library) -> None:
            library.check_library_files_for_changes()
            library.prepare_for_run()

        # Get list of all libraries
        library_list = self.library_container.get()
        # Default number of threads
        num_threads = 1
        # Check if threading is enabled, i.e. > 0
        if self.settings.get_num_threads() > 0:
            if len(library_list) > 0:
                num_threads = len(library_list)

        # Execute using 1 or more threads
        with ThreadPool(num_threads) as pool:
            pool.map(library_prepare, library_list)

    # ====================================================================
    # Container methods
    # ====================================================================

    def _get_library_container(self) -> 'Container':
        '''
        :rtype: Container
        :return: Container with defined libraries.
        '''
        return self.library_container

    def _get_testgroup_container(self,
                                 testgroup_name: str,
                                 create_if_not_found: bool=True) -> 'Container':
        '''
        Locate the testgroup container, or get a new if not found.

        :param testgroup_name: Name of testgroup container to get/create
        :type testgroup_name: str
        :param create_if_not_found: Selects if a missing container should be created.
        :type create_if_not_found: bool

        :rtype: Container
        :return: Testgroup container
        '''
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

    def _get_library_object(self,
                            library_name: str,
                            create_new_if_missing: bool=True,
                            precompiled: bool=False) -> 'Library':
        '''
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
        '''
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

    def _organize_libraries_by_dependency(self) -> None:
        """
        Organize libraries by dependency order.

        :rtype: bool
        :return: Status of setting up library dependencies.
        """
        # Skip if no libraries have changes.
        lib_changes = any(lib.get_need_compile()
                          for lib in self.library_container.get())
        if lib_changes is False:
            return True

        # Organize by dependency - this value of i corresponds to
        # how many values were sorted.
        num_libraries = self.library_container.num_elements()
        libraries = self.library_container.get()

        swapped = True
        while swapped:
            swapped = False

            for i in range(num_libraries):
                # Assume that the first item of the unsorted
                # segment has no dependencies.
                lowest_value_index = i
                # This loop iterates over the unsorted items.
                for j in range(i + 1, num_libraries):
                    check_lib = libraries[j]
                    with_lib = libraries[lowest_value_index]

                    if check_lib.get_name() in with_lib.get_lib_dep():
                        if with_lib.get_name() in check_lib.get_lib_dep():
                            self.logger.error('Recursive library dependency: %s and %s.' % (
                                check_lib.get_name(), with_lib.get_name()))
                            continue
                        lowest_value_index = j
                # Swap values of the lowest unsorted element with the
                # first unsorted element.
                if i != lowest_value_index:
                    self.logger.debug(
                        f"Swapping: {check_lib.get_name()} <-> {with_lib.get_name()}.")
                    (libraries[i], libraries[lowest_value_index]) = \
                        (libraries[lowest_value_index], libraries[i])
                    swapped = True

    def _save_project_to_disk(self,
                              lib_cont: 'Container',
                              generic_cont: 'Container',
                              tg_cont: 'Container',
                              tg_col_cont: 'Container',
                              settings: 'HDLRegressionSettings', reset: bool=True):
        '''
        Save project structure to files.

        :param lib_cont: Container obj with all library information.
        :type lib_cont: Container
        :param generic_cont: Container obj with all generic information.
        :type generic_cont: Container
        :param tg_cont: Container obj with all test group information.
        :type tg_cont: Container
        :param tg_col_cont: Container obj with all testgroup containers information.
        :type tg_col_cont: Container
        :parsm settings: All run settings.
        :type settings: HDLRegressionSettings
        :param reset: Enables resetting of all HDLRegressionSettings obj settings.
        :type reset: bool
        '''

        # Helper method
        def _dump(container, filename):
            filename = os.path.join(os.getcwd(), 'hdlregression', filename)
            filename = os_adjust_path(filename)
            dump_file = open(filename, 'wb')
            pickle.dump(container,
                        dump_file,
                        pickle.HIGHEST_PROTOCOL)
            dump_file.close()

        if reset:
            # Do not save argument settings, i.e. this will make next run
            # behave as selected with previous run arguments.
            settings = self.settings_config.unset_argument_settings(settings)

        _dump(lib_cont, 'library.dat')
        _dump(generic_cont, 'generic.dat')
        _dump(tg_cont, 'testgroup.dat')
        _dump(tg_col_cont, 'testgroup_collection.dat')
        _dump(settings, 'settings.dat')

    def _load_project_from_disk(self) -> tuple:
        '''
        Load project structure from files.

        :rtype: Container
        :return lib_cont: Structure with all library information.
        :rtype: Container
        :return generic_cont: Structure with all generics information.
        :rtype: Container
        :return tg_cont: Structure with all test group information.
        :rtype: Container
        :return tg_col_cont: Structure with all test groups.
        :rtype: HDLRegressionSettings
        :return settings: Obj with all run settings.
        '''
        path = os.getcwd()

        # Helper method
        def _load(container, filename):
            filename = os.path.join(path, 'hdlregression', filename)
            filename = os_adjust_path(filename)
            try:
                load_file = open(filename, 'rb')
                container = pickle.load(load_file)
                load_file.close()
            except:
                self.logger.debug(
                    'Unable to locate container file %s' % (filename))
            return container

        settings_file = os.path.join(path, 'hdlregression', 'settings.dat')
        settings_file = os_adjust_path(settings_file)

        settings = _load(HDLRegressionSettings(), 'settings.dat')
        lib_cont = _load(Container('library'),
                         'library.dat')

        generic_cont = _load(Container('generic'),
                             'generic.dat')
        tg_cont = _load(Container('testgroup'),
                        'testgroup.dat')
        tg_col_cont = _load(Container('testgroup_collection'),
                            'testgroup_collection.dat')

        # Do not load configured generics, testcases or testcase groups when
        # called from runner script, only from GUI
        if self.init_from_gui is False:
            generic_cont.empty_list()
            tg_cont.empty_list()
            tg_col_cont.empty_list()

        if os.path.isfile(settings_file):
            if settings.get_simulator_name() != self.settings.get_simulator_name()\
                    and not self.settings.get_clean():
                self.logger.error('HDLRegression cache was run using %s simulator, '
                                  'current simulator is %s. Aborting' % 
                                  (settings.get_simulator_name(),
                                   self.settings.get_simulator_name()))
                sys.exit(1)

        return (lib_cont,
                generic_cont,
                tg_cont,
                tg_col_cont,
                settings)

# pylint: disable=unused-argument


def exit_handler(signal_received, frame):
    ''' Gracefully exit HDLRegression when CTRL-C is pressed. '''
    print('\nHDLRegression run aborted - exiting.')
    print('''
Note! Aborting HDLRegression can create errors in the run structure, thus
the next run should include the "-c" clean argument.''')
    os._exit(0)

