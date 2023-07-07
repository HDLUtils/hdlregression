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
import re
import time
from abc import abstractmethod
from threading import Thread
from queue import Queue
from shutil import copytree

from .testbuilder import TestBuilder
from ..construct.hdl_modules_pkg import *
from .cmd_runner import CommandRunner
from ..report.logger import Logger
from ..hdlregression_pkg import convert_from_millisec
from ..hdlregression_pkg import os_adjust_path
from .hdltests import VHDLTest, VerilogTest
from ..construct.hdlfile import VHDLFile, VerilogFile


class HDLRunnerError(Exception):
    pass


class OutputFileError(HDLRunnerError):

    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return "Error when trying to access output file %s." % (self.filename)


class TestOutputPathError(HDLRunnerError):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Error when trying to create test output path %s." % (self.path)


class SimRunner:
    """
    Super class for simulation running:
    - RunnerMentor
    - RunnerGHDL
    - TclRunner
    """

    def __init__(self, project):
        self.logger = Logger(name=__name__, project=project)

        self.env_var = os.environ.copy()
        self.project = project

        # Prepare for saving simulator calls to file
        self.cmd_file_cleaned = False
        self.command_file = os.path.join(
            self.project.settings.get_output_path(), "commands.do"
        )

        # Init list of all test objects
        self.test_list = []

        # Test builder will create a list of test objects to run
        self.testbuilder = TestBuilder(project=project)

        # Prepare regex
        self.RE_UVVM_SUMMARY = None
        self.RE_UVVM_RESULT = None
        self.RE_USER = None
        self._compile_regex()

    def get_test_result(self) -> list:
        pass_list = self._get_pass_test_list()
        fail_list = self._get_fail_test_list()
        not_run_list = self._get_not_run_test_list()
        return [pass_list, fail_list, not_run_list]

    def get_num_pass_test(self) -> int:
        return len(self._get_pass_test_list())

    def get_num_fail_test(self) -> int:
        return len(self._get_fail_test_list())

    def get_num_pass_with_minor_alerts_test(self) -> int:
        return len(self._get_pass_with_minor_alert_list())

    def get_num_tests_run(self) -> int:
        """
        Returns the number of all passing and
        failing tests in this run.
        """
        pass_list = self._get_pass_test_list()
        fail_list = self._get_fail_test_list()
        return len(pass_list + fail_list)

    def get_num_tests(self) -> int:
        """
        Returns the number of all possible tests.
        """
        if self.testbuilder:
            return self.testbuilder.get_num_tests()
        return 0

    def _setup_ini(self):
        pass

    def prepare_test_modules_and_objects(self):
        """
        Locate testbench modules and build test objects
        """
        self.testbuilder.build_tb_module_list()
        self.testbuilder.build_list_of_tests_to_run()

    @abstractmethod
    def _compile_library(self, library, force_compile=False) -> "HDLLibrary":
        pass

    def compile_libraries(self):
        """
        Called from HDLRegression() object to:
        1. Check that library folder exist and create and compile library if not.
        2. Check if library require compile and compile library if required.
    
        Returns:
          success(bool): True when no library compilation error.
        """
        # Check if a dependent library has compiled
        lib_container = self.project._get_library_container()

        regular_lib = [
            lib for lib in lib_container.get() if lib.get_is_precompiled() is False
        ]

        # Update libraries for compile if a dependent library require compilation
        for lib in regular_lib:
            dep_lib_compiled = any(
                dep_lib
                for dep_lib in lib.get_lib_obj_dep()
                if dep_lib.get_need_compile() is True
            )
            if dep_lib_compiled is True:
                lib.set_need_compile(True)

        success = True

        # Empty list of libraries compiled in this run
        self.project.settings.reset_library_compile()

        # Check all libraries in project
        for library in regular_lib:
            lib_path_missing = self._check_if_library_path_is_missing(library)
            compile_required = self._check_for_recompile(library, lib_path_missing)
            force_compile = self._check_for_force_compile(library, lib_path_missing)

            if compile_required or force_compile:
                self.logger.info("Compiling library: {}".format(library.get_name()), end=" ")
                compiled_library = self._compile_library(
                    library=library, force_compile=force_compile
                )
                if not compiled_library:
                    self.logger.info(" - FAIL - ", end="\n", color="red")
                    success = False
                    library.set_need_compile(True)
                    self.project.settings.set_return_code(1)
                else:
                    self.logger.info(" - OK - ", end="\n", color="green")
                    library.set_need_compile(False)
                    # Update list of libraries compiled in this run
                    self.project.settings.add_library_compile(library)
                    self.project._get_library_container().update(compiled_library)

        # Update settings with the compilation time
        if success:
            compile_time = time.time()
            self.project.settings.set_compile_time(compile_time)

        return success, self.project._get_library_container()

    def simulate(self) -> bool:
        """
        Collects test objects to run and executes test simulations.
        """

        def run_test(test_queue) -> bool:
            """
            Executes tests from the queue in a separate thread.
            """
            while not test_queue.empty():
                try:
                    test = test_queue.get()
                    self._create_test_folder(test.get_test_path())
                    self._run_terminal_test(test)
                    # Display test information and results
                    print(test.get_terminal_test_details_str())
                    
                    # Print test output in verbose mode
                    if self.project.settings.get_verbose():
                        print(test.get_output())
                    
                    # Present errors
                    if not test.get_result_success():
                        print(test.get_test_error_summary())
                        if self.project.settings.get_stop_on_failure():
                            self.logger.warning("Simulations stopped because of failing testcase.")
                        self.project.settings.set_return_code(1)
                except Exception as e:
                    self.logger.error('An error occurred during test run: {}'.format(e))
                finally:    
                    test_queue.task_done()
    
        # Get tests to run
        self.test_list = self.testbuilder.get_list_of_tests_to_run()
    
        # Backup previous test run results if new tests are run
        if self.test_list:
            self._backup_test_run()
    
        # Start timer
        start_time = round(time.time() * 1000)
    
        num_threads = self._get_number_of_threads()
        if num_threads > 0: 
            self.logger.info(
                "Running {} out of {} test(s) using {} thread(s).".format(self.get_num_tests_run(),
                                                                          self.get_num_tests(),
                                                                          num_threads))

            # create test queue for threads to operate with
            test_queue = Queue()
            for test in self.test_list:
                test_queue.put(test)

            # run threads
            for _ in range(num_threads):
                thread = Thread(target=run_test, args=(test_queue,))
                thread.daemon = True
                thread.start()

            # wait for test queue to finish
            test_queue.join()

            # Calculate and update timing
            finish_time = round(time.time() * 1000)
            elapsed_time = finish_time - start_time
            self.project.settings.set_sim_time(elapsed_time)

            # Write mapping file for run tests.
            self._write_test_mapping(self.test_list)
    
        return True

    # ===================================================================================================
    #
    # Non-public methods
    #
    # ===================================================================================================

    def _get_pass_test_list(self) -> list:
        if self.test_list is None:
            self.test_list = self._get_test_list()

        pass_list = [
            test.get_test_id_string()
            for test in self.test_list
            if test.get_result_success() is True
        ]
        return pass_list

    def _get_fail_test_list(self) -> list:
        if self.test_list is None:
            self.test_list = self._get_test_list()

        fail_list = [
            test.get_test_id_string()
            for test in self.test_list
            if test.get_result_success() is False
        ]
        return fail_list

    def _get_pass_with_minor_alert_list(self) -> list:
        if self.test_list is None:
            self.test_list = self._get_test_list()

        pass_with_minor_alerts_list = [
            test.get_test_id_string()
            for test in self.test_list
            if test.get_no_minor_alerts() is False
        ]
        return pass_with_minor_alerts_list

    def _get_not_run_test_list(self) -> list:
        if not self.test_list:
            self.test_list = self.testbuilder.get_list_of_tests_to_run()

        test_list = [
            test.get_test_id_string()
            for test in self.test_list
            if test.get_has_been_run() is False
        ]
        return test_list

    def _get_test_list(self) -> list:
        return self.testbuilder.get_list_of_tests_to_run()

    @classmethod
    @abstractmethod
    def _is_simulator(cls, simulator) -> bool:
        pass

    def _check_if_library_path_is_missing(self, library) -> bool:
        lib_base_path = os.path.join(self.project.settings.get_output_path(), "library")
        # Library folder does not exist or library recompile required
        lib_path = os.path.join(lib_base_path, library.get_name())
        if not os.path.isdir(lib_path) and not self._is_simulator("ghdl"):
            return True
        else:
            return False

    def _check_for_recompile(self, library, lib_path_missing) -> bool:
        # Check if library compile is needed
        compile_required = lib_path_missing or library.get_need_compile()
        return compile_required

    def _check_for_force_compile(self, library, lib_path_missing) -> bool:
        # Check if library compile is requested
        force_compile = (
            self.project.settings.get_gui_compile_all()
            or self.project.settings.get_force_recompile()
        )
        # Check if library should not compile on request
        force_compile = (
            False if library.get_never_recompile() is True else force_compile
        )
        # Library needs to be compiled at least once - even when set to never recompile.
        force_compile = True if lib_path_missing is True else force_compile
        return force_compile

    @staticmethod
    def _divide_test_list_to_num_threads(test_list, num_threads) -> list:
        """
        Divides the test_list to 'num_threads' parts.

        Returns
            test_list (list) : a list of 'num_threads' lists of tests.
        """

        # Internal method for dividing test list
        def devide_list_for_threads(lst, sz):
            return [lst[i: i + sz] for i in range(0, len(lst), sz)]

        if num_threads > 1:
            devided_list = devide_list_for_threads(test_list, num_threads)
            test_list = []
            for item in devided_list:
                test_list += item
        return test_list

    def _get_number_of_threads(self) -> int:
        """
        Adjusts the number of threads to run simulations by
        checking if CLI argument was entered, and scaled to
        the number of tests to run.

        Returns:
            num_threads (int) : number of threads to run simulations.
        """
        # Default number of threads
        num_threads = 1
        # Adjust to one thread per parser if threading is enabled
        if self.project.settings.get_num_threads() > 0:
            num_threads = self.project.settings.get_num_threads()
            # Adjust that we do not use more threads than required
            if self.get_num_tests_run() < num_threads:
                num_threads = self.get_num_tests_run()
        return num_threads

    def _compile_regex(self):
        # Setup regex
        ID_UVVM_SUMMARY = r"FINAL SUMMARY OF ALL ALERTS"
        ID_UVVM_RESULT_ALL_PASS = r">> Simulation SUCCESS: No mismatch between counted and expected serious alerts"
        ID_UVVM_RESULT_PASS_WITH_MINOR = r", but mismatch in minor alerts"
        self.RE_UVVM_SUMMARY = re.compile(ID_UVVM_SUMMARY, flags=re.IGNORECASE)
        self.RE_UVVM_RESULT_ALL_PASS = re.compile(
            ID_UVVM_RESULT_ALL_PASS, flags=re.IGNORECASE
        )
        self.RE_UVVM_RESULT_PASS_WITH_MINOR = re.compile(
            ID_UVVM_RESULT_PASS_WITH_MINOR, flags=re.IGNORECASE
        )

        if self.project.settings.get_result_check_str():
            self.RE_USER = re.compile(
                self.project.settings.get_result_check_str(), flags=re.IGNORECASE
            )

    # ---------------------------------------------------------
    # File handling
    # ---------------------------------------------------------
    def _backup_test_run(self) -> None:
        """
        Check if there has been a previous test run and move
        those test results to a backup folder.
        """
    
        def backup_test_results(backup_folder):
            try:
                if keep_code_coverage:
                    self.logger.info("Backing up previous test run to: {}.".format(backup_folder))
                    copytree(self.project.settings.get_test_path(), backup_folder)
                else:
                    self.logger.info("Moving previous test run to: {}.".format(backup_folder))
                    os.rename(self.project.settings.get_test_path(), backup_folder)
            except OSError as error:
                self.logger.warning("Unable to backup tests: {}".format(error))
    
        keep_code_coverage = self.project.settings.get_keep_code_coverage()
    
        if self.project.settings.get_time_of_run() and os.path.exists(self.project.settings.get_test_path()):
            backup_folder = "{}_{}".format(self.project.settings.get_test_path(), self.project.settings.get_time_of_run())
    
            if not os.path.exists(backup_folder):
                backup_test_results(backup_folder)
            else:
                self.logger.warning("Backup folder {} already exists.".format(backup_folder))

    def _write_test_mapping(self, tests) -> None:
        """
        Create a test and folder mapping file to locate
        test run with hashed test run folders.
        """
    
        def write_test_mapping_to_file(test_mapping_file):
            try:
                with open(test_mapping_file, "a+") as mapping_file:
                    for test in tests:
                        mapping_file.write(test.get_folder_to_name_mapping())
            except Exception as error:
                self.logger.warning("Unable to write test mapping file {}. Error: {}".format(test_mapping_file, error))
    
        self.logger.debug("Writing test mapping CSV file.")
        test_mapping_file = os.path.join(self.project.settings.get_test_path(), "test_mapping.csv")
        
        write_test_mapping_to_file(test_mapping_file)

    # ---------------------------------------------------------
    # Compilation and simulating
    # ---------------------------------------------------------

    def _get_simulator_executable(self, sim_exec="vsim") -> str:
        """
        Returns the full path for the simulator executor file, e.g.
        vsim, vlib etc.
        """
        executor = self.project.settings.get_simulator_exec(sim_exec)
        if executor is None:
            self.logger.warning("Invalid executor call: {}".format(sim_exec))
            return sim_exec
        else:
            sim_exec = os_adjust_path(executor)
            return sim_exec

    def _get_simulator_error_regex(self):
        pass
      
    def _get_simulator_warning_regex(self):
        pass

    # ---------------------------------------------------------
    # Command
    # ---------------------------------------------------------

    def _save_cmd(self, cmd) -> None:
        """
        Saves simulator call commands to file.
        """
    
        def create_cmd_file():
            try:
                with open(self.command_file, "w"):
                    pass
            except IOError as e:
                self.logger.error("Error creating command file: {}".format(e))
                return False
            return True
    
        def append_cmd_to_file(cmd_str):
            try:
                with open(self.command_file, "a") as file:
                    file.write("{}\n".format(cmd_str))
            except IOError as e:
                self.logger.error("Error appending to command file: {}".format(e))
    
        if not self.cmd_file_cleaned:
            self.cmd_file_cleaned = True
            output_dir = self.project.settings.get_output_path()
    
            if not os.path.isdir(output_dir):
                try:
                    os.mkdir(output_dir)
                except OSError as e:
                    self.logger.error("Error creating output directory: {}".format(e))
                    return
    
            if not create_cmd_file():
                return
    
        if isinstance(cmd, list):
            cmd = " ".join(map(str, cmd))
    
        append_cmd_to_file(cmd)

    def _get_error_detection_str(self) -> str:
        return ""

    def _get_ignored_error_detection_str(self) -> str:
        return ""

    def _run_cmd(self, command, path="./", output_file=None, test=None) -> bool:
        """
        Runs selected command(s), checks for simulator warning/error.
    
        Param:
            command(lst): command string as list.
            path(str): path to run command
            output_file(str): name of file to put output
    
        Returns:
            bool: True if command was successful, else False
        """
        
        def check_has_line_warning(line) -> bool:
            return bool(re.search(self._get_simulator_warning_regex(), line))

        def check_has_line_error(line) -> bool:
            return bool(re.search(self._get_simulator_error_regex(), line))

        def show_errors_and_warnings() -> (tuple):
            # override
            if self.project.settings.get_show_err_warn_output() is True:
                return (True, True)
            # compilation
            elif test is None:
                return (True, True)
            # simulation
            else:
                return (False, False)

        # Write command to file
        self._save_cmd(command)

        cmd_runner = CommandRunner(project=self.project)

        if test is not None:
            test.clear_output()

        success = True

        (show_sim_errors, show_sim_warnings) = show_errors_and_warnings()

        for line, success in cmd_runner.run(command=command,
                                            path=path,
                                            env=self.env_var,
                                            output_file=output_file):
            line = line.strip()

            # Sim output direction
            self._output_handler(test, line)

            if check_has_line_error(line) is True or not success:
                if show_sim_errors is True:
                    self.logger.error(line)
                if test is not None:
                    test.inc_num_sim_errors()

            if check_has_line_warning(line) is True:
                if show_sim_warnings is True:
                    self.logger.warning(line)
                if test is not None:
                    test.inc_num_sim_warnings()

        return success

    def _output_handler(self, test, line):
        """
        Directs simulation output to the terminal or the
        test object.
        """
        if line:
            single_sim_thread = self._get_number_of_threads() < 2
            if test:
                test.add_output(line)

            if self.project.settings.get_verbose() and single_sim_thread:
                print(line)

    # ---------------------------------------------------------
    # Testbench and simulations
    # ---------------------------------------------------------

    @abstractmethod
    def _write_run_do_file(self, test, generic_call, module_call):
        pass

    @abstractmethod
    def _simulate(self, test, generic_call, module_call) -> tuple:
        pass

    def _run_terminal_test(self, test) -> None:
        """
        Run test in terminal mode
        """

        def get_module_call():
            if self._is_simulator("ghdl"):
                return architecture_name
            elif self._is_simulator("nvc"):
                return "{}-{}".format(test.get_name(), architecture_name)
            else:
                if test.get_is_vhdl():
                    return "{}.{}({})".format(lib_name, test.get_name(), architecture_name)
                else:
                    return "{}.{}".format(lib_name, test.get_name())

        def get_descriptive_test_name():
            if self._is_simulator("ghdl") or self._is_simulator("nvc"):
                name = "{}.{}".format(lib_name, test.get_name())
                return "{}({})".format(name, architecture_name) if test.get_is_vhdl() else name
            else:
                return module_call

        def run_simulation():
            sim_start_time = round(time.time() * 1000)
            terminal_output_string = self._create_terminal_test_info_output_string(test, descriptive_test_name)
            test.set_test_id_string(terminal_output_string)

            self._write_run_do_file(test=test, generic_call=gen_call, module_call=module_call)

            self._simulate(test=test, generic_call=gen_call, module_call=module_call)
            self._check_test_result(test=test, sim_start_time=sim_start_time)

            test.set_folder_to_name_mapping(descriptive_test_name)

        gen_call = test.get_gc_str()
        architecture_name = "" if not test.get_is_vhdl() else test.get_arch().get_name()
        lib_name = test.get_library().get_name()

        module_call = get_module_call()
        descriptive_test_name = get_descriptive_test_name()

        run_simulation()

    @staticmethod
    def _create_test_folder(path) -> None:
        """
        Create the test folder for this test run.
        """
        try:
            os.makedirs(path, exist_ok=True)
        except:
            raise TestOutputPathError(path)

    def _is_uvvm_summary_start(self, line):
        return re.search(self.RE_UVVM_SUMMARY, line)

    def _is_uvvm_simulation_pass(self, line):
        return re.search(self.RE_UVVM_RESULT_ALL_PASS, line)

    def _has_minor_alerts(self, line):
        return re.search(self.RE_UVVM_RESULT_PASS_WITH_MINOR, line)

    def _is_user_selected_result_match(self, line):
        return re.search(self.RE_USER, line)

    def _check_file_content(self, lines):
        """
        Check transcript lines for PASS criteria.
        """
        summary_found = False
        test_ok = False
        test_ok_no_minor_alerts = True
    
        use_user_selected_result = bool(self.project.settings.get_result_check_str())
    
        if lines is not None:
            for line in lines:
                if not use_user_selected_result:
                    if not summary_found and self._is_uvvm_summary_start(line):
                        summary_found = True
                    elif summary_found:
                        if self._is_uvvm_simulation_pass(line):
                            test_ok = True
                            if self._has_minor_alerts(line):
                                test_ok_no_minor_alerts = False
                            break
                elif self._is_user_selected_result_match(line):
                    test_ok = True
                    break
        return test_ok, test_ok_no_minor_alerts

    def _check_test_result(self, test, sim_start_time) -> None:
        """
        Check test run transcript file for passing/failing test.
        Add passing/failing test to test lists and present to transcript.
        """

        def log_checking():
            result_check_str = self.project.settings.get_result_check_str()
            if result_check_str:
                self.logger.debug("Checking for {}.".format(result_check_str))
            else:
                self.logger.debug("Checking for UVVM summary report")
    
        def format_test_result(test_ok, test_ok_no_minor_alerts):
            if test_ok:
                test_str_result = self.logger.green() + "PASS"
                if not test_ok_no_minor_alerts:
                    test_str_result += self.logger.yellow() + " (with minor alerts)"
            else:
                test_str_result = self.logger.red() + "FAIL" 
            return test_str_result + self.logger.reset_color()
          
        def format_number_of_sim_errors_and_warnings(test):
            sim_errors = test.get_num_sim_errors()
            sim_warnings = test.get_num_sim_warnings()
            if sim_errors > 0 or sim_warnings > 0:
                return "\nTest run: sim_errors={}, sim_warnings={}".format(sim_errors, sim_warnings)
            else:
                return ""

        def format_test_details_string(test_str_result, sim_num_errors_and_warnings_str):
            sim_end_time = round(time.time() * 1000)
            elapsed_time = sim_end_time - sim_start_time
            sim_sec, sim_min, sim_hrs = convert_from_millisec(elapsed_time)
            return "{}{} ({}h:{}m:{}s){}.\n".format(
                test.get_terminal_test_string(),
                test_str_result,
                sim_hrs,
                sim_min,
                sim_sec,
                sim_num_errors_and_warnings_str
            )
        
        def update_test_status_and_info(test):
            (test_ok, test_ok_no_minor_alerts) = self._check_file_content(test.get_output_no_format())
            test_str_result = format_test_result(test_ok, test_ok_no_minor_alerts)
            sim_num_errors_and_warnings_str = format_number_of_sim_errors_and_warnings(test)
            test_details_str = format_test_details_string(test_str_result, sim_num_errors_and_warnings_str)
            test.set_terminal_test_details_str(test_details_str)
            test.set_result_success(test_ok, no_minor_alerts=test_ok_no_minor_alerts)
            test.set_has_been_run(True)

        log_checking()
        update_test_status_and_info(test)

    def _create_terminal_test_info_output_string(self, test, descriptive_test_name) -> str:
        """
        Create a testcase name based on entity, architecture, test, and generics.
        """

        def get_generics_string(test) -> str:
            generics = test.get_gc_str(filter_testcase_id=True)
            if generics:
                return generics.replace("-g", "")
            return ""

        def build_test_string_base():
            return descriptive_test_name.replace("(", ".").replace(")", "")

        def build_testcase_string():
            testcase = test.get_tc()
            return ".{}".format(testcase) if testcase else ""

        def build_test_id_string():
            return " (test_id: {})".format(test.get_test_id_number())

        def build_generics_section():
            generics = get_generics_string(test)
            return "\nGenerics: {}".format(generics) if generics else ""

        def build_timing_section():
            timing = test.get_netlist_timing()
            return "\nTiming: {}".format(timing) if timing else ""

        test_string_base = build_test_string_base()
        testcase_string = build_testcase_string()
        test_id_string = build_test_id_string()
        generics_section = build_generics_section()
        timing_section = build_timing_section()

        return "Running: {}{}{}{}{}\nResult: ".format(test_string_base,
                                                      testcase_string,
                                                      test_id_string,
                                                      generics_section,
                                                      timing_section)
