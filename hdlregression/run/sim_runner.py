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

if __package__ is None or __package__ == '':
    from testbuilder import TestBuilder
    from hdl_modules_pkg import *
    from cmd_runner import CommandRunner
    from logger import Logger
    from hdlregression_pkg import convert_from_millisec
    from hdlregression_pkg import os_adjust_path
    from hdltests import VHDLTest, VerilogTest
    from hdlfile import VHDLFile, VerilogFile

else:
    from .testbuilder import TestBuilder
    from ..struct.hdl_modules_pkg import *
    from .cmd_runner import CommandRunner
    from ..report.logger import Logger
    from ..hdlregression_pkg import convert_from_millisec
    from ..hdlregression_pkg import os_adjust_path
    from .hdltests import VHDLTest, VerilogTest
    from ..struct.hdlfile import VHDLFile, VerilogFile


class HDLRunnerError(Exception):
    pass


class OutputFileError(HDLRunnerError):
    def __init__(self, filename):
        self.filename = filename

    def __str__(self):
        return 'Error when trying to access output file %s.' % (self.filename)


class TestOutputPathError(HDLRunnerError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return 'Error when trying to create test output path %s.' % (self.path)


class SimRunner:
    '''
    Super class for simulation running:
    - RunnerMentor
    - RunnerGHDL
    - TclRunner
    '''

    def __init__(self, project):
        self.logger = Logger(name=__name__, project=project)

        self.env_var = os.environ.copy()
        self.project = project

        # Prepare for saving simulator calls to file
        self.cmd_file_cleaned = False
        self.command_file = os.path.join(
            self.project.settings.get_output_path(), "commands.do")

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
        fail_list = self._get_fail_pass_list()
        return [pass_list, fail_list]

    def get_num_pass_test(self) -> int:
        return len(self._get_pass_test_list())

    def get_num_fail_test(self) -> int:
        return len(self._get_fail_pass_list())

    def get_num_pass_with_minor_alerts_test(self) -> int:
        return len(self._get_pass_with_minor_alert_list())

    def get_num_tests_run(self) -> int:
        '''
        Returns the number of all passing and
        failing tests in this run.
        '''
        pass_list = self._get_pass_test_list()
        fail_list = self._get_fail_pass_list()
        return len(pass_list + fail_list)

    def get_num_tests(self) -> int:
        '''
        Returns the number of all possible tests.
        '''
        if self.testbuilder:
            return self.testbuilder.get_num_tests()
        return 0

    def _setup_ini(self):
        pass

    def prepare_test_modules_and_objects(self):
        '''
        Locate testbench modules and build test objects
        '''
        self.testbuilder.build_tb_module_list()
        self.testbuilder.build_list_of_tests_to_run()

    @abstractmethod
    def _compile_library(self, library, force_compile=False) -> 'HDLLibrary':
        pass

    def compile_libraries(self):
        '''
        Called from HDLRegression() object to:
        1. Check that library folder exist and create and compile library if not.
        2. Check if library require compile and compile library if required.

        Returns:
          success(bool): True when no library compilation error.
        '''
        # Check if a dependent library has compiled
        lib_container = self.project._get_library_container()

        regular_lib = [lib for lib in lib_container.get() if lib.get_is_precompiled() is False]

        # Update libraries for compile if a dependent library require compilation
        for lib in regular_lib:
            dep_lib_compiled = any(dep_lib for dep_lib in lib.get_lib_obj_dep(
            ) if dep_lib.get_need_compile() is True)
            if dep_lib_compiled is True:
                lib.set_need_compile(True)

        success = True

        # Empty list of libraries compiled in this run
        self.project.settings.reset_library_compile()

        # Check all libraries in project
        # for library in lib_container.get():
        for library in regular_lib:
            lib_path_missing = self._check_if_library_path_is_missing(library)
            compile_required = self._check_for_recompile(library, lib_path_missing)
            force_compile = self._check_for_forcompile(library, lib_path_missing)

            if compile_required or force_compile:
                self.logger.info('Compiling library: %s' %
                                 (library.get_name()), end=' ')
                compiled_library = self._compile_library(
                    library=library, force_compile=force_compile)
                if not compiled_library:
                    self.logger.info(' - FAIL - ', end='\n', color='red')
                    success = False
                    library.set_need_compile(True)
                else:
                    self.logger.info(' - OK - ', end='\n', color='green')
                    library.set_need_compile(False)
                    # Update list of libraries compiled in this run
                    self.project.settings.add_library_compile(library)
                    self.project._get_library_container().update(compiled_library)

        # Update settings with the compilation time
        if success:
            compile_time = time.time()
            self.project.settings.set_compile_time(compile_time)

        return (success, self.project._get_library_container())

    def simulate(self) -> bool:
        '''
        Collects test objects to run and executes
        test simulations.
        '''

        def run_test(test_queue) -> bool:
            while not test_queue.empty():
                test = test_queue.get()

                self._create_test_folder(test.get_test_path())
                self._run_terminal_test(test)

                # Display test information and results
                print(test.get_terminal_test_details_str())

                # Print test output in verbose mode
                if self.project.settings.get_verbose() is True:
                    print(test.get_output())

                # Present errors
                if test.get_result_success() is False:
                    print(test.get_test_error_summary())
                    if self.project.settings.get_stop_on_failure():
                        self.logger.warning(
                            'Simulations stopped because of failing testcase.')
                test_queue.task_done()


        # default
        success = True

        # Get tests to run
        self.test_list = self.testbuilder.get_list_of_tests_to_run()

        # Backup previous test run results if new tests are run
        if self.test_list:
            self._backup_test_run()

        # Start timer
        start_time = round(time.time() * 1000)

        num_threads = self._get_number_of_threads()
        if num_threads == 0:
            return success

        self.logger.info('Running %d out of %d test(s) using %d thread(s).' % (self.get_num_tests_run(),
                                                                               self.get_num_tests(),
                                                                               num_threads))

        # create test queue for threads to operate with
        test_queue = Queue()
        for test in self.test_list:
            test_queue.put(test)

        # run threads
        for _ in range(num_threads):
            thread = Thread(target=run_test, args=(test_queue, ))
            thread.daemon = True
            thread.start()

        # wait for test queue to finish
        test_queue.join()


        # Calculate and update timing
        finish_time = round(time.time() * 1000)
        elapsed_time = finish_time - start_time
        sim_sec, sim_min, sim_hrs = convert_from_millisec(elapsed_time)
        self.logger.info('Simulation run time: %dh:%dm:%ds.' %
                         (sim_hrs, sim_min, sim_sec))
        self.project.settings.set_sim_time(elapsed_time)

        # Write mapping file for run tests.
        self._write_test_mapping(self.test_list)
        return success

# ===================================================================================================
#
# Non-public methods
#
# ===================================================================================================

    def _get_pass_test_list(self) -> list:
        pass_list = [test.get_test_id_string()
                     for test in self.test_list if test.get_result_success() is True]
        return pass_list

    def _get_fail_pass_list(self) -> list:
        fail_list = [test.get_test_id_string()
                     for test in self.test_list if test.get_result_success() is False]
        return fail_list

    def _get_pass_with_minor_alert_list(self) -> list:
        pass_with_minor_alerts_list = [test.get_test_id_string(
        ) for test in self.test_list if test.get_no_minor_alerts() is False]
        return pass_with_minor_alerts_list

    @classmethod
    @abstractmethod
    def _is_simulator(cls, simulator) -> bool:
        pass

    def _check_if_library_path_is_missing(self, library) -> bool:
        lib_base_path = os.path.join(self.project.settings.get_output_path(), 'library')
        # Library folder does not exist or library recompile required
        lib_path = os.path.join(lib_base_path, library.get_name())
        if not os.path.isdir(lib_path) and not self._is_simulator('ghdl'):
            return True
        else:
            return False

    def _check_for_recompile(self, library, lib_path_missing) -> bool:
        # Check if library compile is needed
        compile_required = (lib_path_missing or library.get_need_compile())
        return compile_required

    def _check_for_forcompile(self, library, lib_path_missing) -> bool:
        # Check if library compile is requested
        force_compile = (self.project.settings.get_gui_compile_all() or self.project.settings.get_force_recompile())
        # Check if library should not compile on request
        force_compile = False if library.get_never_recompile() is True else force_compile
        # Library needs to be compiled at least once - even when set to never recompile.
        force_compile = True if lib_path_missing is True else force_compile
        return force_compile

    @staticmethod
    def _divide_test_list_to_num_threads(test_list, num_threads) -> list:
        '''
        Divides the test_list to 'num_threads' parts.

        Returns
            test_list (list) : a list of 'num_threads' lists of tests.
        '''
        # Internal method for dividing test list
        def devide_list_for_threads(lst, sz): return [
            lst[i:i+sz] for i in range(0, len(lst), sz)]

        if num_threads > 1:
            devided_list = devide_list_for_threads(test_list, num_threads)
            test_list = []
            for item in devided_list:
                test_list += item
        return test_list

    def _get_number_of_threads(self) -> int:
        '''
        Adjusts the number of threads to run simulations by
        checking if CLI argument was entered, and scaled to
        the number of tests to run.

        Returns:
            num_threads (int) : number of threads to run simulations.
        '''
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
        ID_UVVM_SUMMARY = r'FINAL SUMMARY OF ALL ALERTS'
        ID_UVVM_RESULT_ALL_PASS = r'>> Simulation SUCCESS: No mismatch between counted and expected serious alerts'
        ID_UVVM_RESULT_PASS_WITH_MINOR = r', but mismatch in minor alerts'
        self.RE_UVVM_SUMMARY = re.compile(ID_UVVM_SUMMARY, flags=re.IGNORECASE)
        self.RE_UVVM_RESULT_ALL_PASS = re.compile(
            ID_UVVM_RESULT_ALL_PASS, flags=re.IGNORECASE)
        self.RE_UVVM_RESULT_PASS_WITH_MINOR = re.compile(
            ID_UVVM_RESULT_PASS_WITH_MINOR, flags=re.IGNORECASE)

        if self.project.settings.get_result_check_str():
            self.RE_USER = re.compile(
                self.project.settings.get_result_check_str(), flags=re.IGNORECASE)

    def _gui_mode(self) -> bool:
        '''
        Return True if gui mode is possible with this simulator
        '''
        # Check with sub-class that simulator is not GHDL
        simulator_has_gui = not (self._is_simulator('ghdl') or self._is_simulator('nvc'))
        # Check if gui mode is enabled in config
        gui_mode_enabled = self.project.settings.get_gui_mode()
        return (simulator_has_gui and gui_mode_enabled)

    # ---------------------------------------------------------
    # File handling
    # ---------------------------------------------------------
    def _backup_test_run(self) -> None:
        '''
        Check if there has been a previous test run and move
        those test results to a backup folder.
        '''
        keep_code_coverage = self.project.settings.get_keep_code_coverage()

        if self.project.settings.get_time_of_run() and os.path.exists(self.project.settings.get_test_path()):
            backup_folder = self.project.settings.get_test_path(
            ) + '_' + self.project.settings.get_time_of_run()
            if not os.path.exists(backup_folder):

                try:
                    if keep_code_coverage is True:
                        self.logger.info(
                            "Backup previous test run to: %s." % (backup_folder))
                        copytree(self.project.settings.get_test_path(),
                                 backup_folder)
                    else:
                        self.logger.info(
                            "Moving previous test run to: %s." % (backup_folder))
                        os.rename(self.project.settings.get_test_path(),
                                  backup_folder)
                except OSError as error:
                    self.logger.warning('Unable to backup tests: %s' % (error))
            else:
                self.logger.warning(
                    "Backup folder %s already exist." % (backup_folder))

    def _write_test_mapping(self, tests) -> None:
        '''
        Create a test and folder mapping file to locate
        test run with hashed test run folders.
        '''
        # Create mapping of test run with folder
        self.logger.debug("Writing test mapping CSV file.")
        test_mapping_file = os.path.join(
            self.project.settings.get_test_path(), 'test_mapping.csv')
        try:
            with open(test_mapping_file, 'a+') as mapping_file:
                for test in tests:
                    mapping_file.write(test.get_folder_to_name_mapping())
        except:
            self.logger.warning(
                "Unable to write test mapping file %s." % (test_mapping_file))

    # ---------------------------------------------------------
    # Compilation and simulating
    # ---------------------------------------------------------

    def _get_simulator_executable(self, sim_exec='vsim') -> str:
        if self.project.settings.get_simulator_path():
            sim_exec = os.path.join(
                self.project.settings.get_simulator_path(), sim_exec)
            if os.path.isdir(self.project.settings.get_simulator_path()):
                sim_exec = os_adjust_path(sim_exec)
            else:
                self.logger.warning(
                    'Simulator exec %s not valid.' % (sim_exec))
        return sim_exec

    # ---------------------------------------------------------
    # Command
    # ---------------------------------------------------------

    def _save_cmd(self, cmd) -> None:
        '''
        Saves simulator call commands to file.
        '''
        if not(self.cmd_file_cleaned):
            self.cmd_file_cleaned = True
            output_dir = self.project.settings.get_output_path()
            if not os.path.isdir(output_dir):
                os.mkdir(output_dir)
            # Create file
            with open(self.command_file, 'w'):
                pass

        if isinstance(cmd, list):
            cmd = ' '.join(map(str, cmd))
        with open(self.command_file, 'a') as file:
            file.write(cmd + '\n')

    def _run_cmd(self, command, path='./', output_file=None, test=None) -> bool:
        '''
        Runs selected command(s), checks for simulator warning/error.

        Param:
            command(lst): command string as list.
            path(str): path to run command
            output_file(str): name of file to put output


        Returns:
            bool: True if command was successful, else False
        '''
        # Write command to file
        self._save_cmd(command)

        cmd_runner = CommandRunner(project=self.project)
        line = ''

        # Set simulator error detection
        if self._is_simulator("ghdl"):
            error_detection_str = r'[\r\n\s]?ghdl:'
        elif self._is_simulator("nvc"):
            error_detection_str = r'^[\r\n\s]?.*: (error|fatal): '
        else:
            error_detection_str = r'^[\r\n\s]?\*\*\sError[\s+]?[:]?'

        re_error_detection_str = re.compile(error_detection_str,
                                            flags=re.IGNORECASE | re.MULTILINE)

        if test is not None:
            test.clear_output()

        error_detected = False
        for line, success in cmd_runner.run(command=command,
                                            path=path,
                                            env=self.env_var,
                                            output_file=output_file):

            line = line.strip()

            # Sim output direction
            self._direct_sim_output(test, line)

            # Error detection
            if re.search(re_error_detection_str, line) or not success:
                if not error_detected:
                    error_detected = True
                    self.logger.error('') # Add newline
                self.logger.error(line)

        return (error_detected is False)

    def _direct_sim_output(self, test, line):
        '''
        Directs simulation output to the terminal or the
        test object.
        '''
        if line:
            single_sim_thread = (self._get_number_of_threads() < 2)
            if (self.project.settings.get_verbose() and single_sim_thread):
                print(line)
            elif test is not None:
                test.add_output(line)

    # ---------------------------------------------------------
    # Testbench and simulations
    # ---------------------------------------------------------

    @abstractmethod
    def _simulate(self, test, generic_call, module_call) -> bool:
        pass

    def _run_terminal_test(self, test) -> None:
        '''
        Run test in terminal mode
        '''
        gen_call = ''
        architecture_name = ''
        if test.get_is_vhdl():
            architecture = test.get_arch()
            architecture_name = architecture.get_name()
            gen_call = test.get_gc_str()
        elif test.get_is_verilog():
            gen_call = test.get_gc_str()

        lib_name = test.get_library().get_name()

        # Create module call: <library_name>.<testbench_name>(<arhitecture_name>)
        if self._is_simulator("ghdl"):
            module_call = architecture_name
        elif self._is_simulator("nvc"):
            module_call = test.get_name() + '-' + architecture_name
        else:
            module_call = lib_name + '.' + test.get_name()
            if test.get_is_vhdl():
                module_call += '(' + architecture_name + ')'

        if self._is_simulator("ghdl") or self._is_simulator("nvc"):
            descriptive_test_name = lib_name + '.' + test.get_name()
            if test.get_is_vhdl():
                descriptive_test_name += '(' + architecture_name + ')'
        else:
            descriptive_test_name = module_call

        sim_start_time = round(time.time() * 1000)

        terminal_output_string = self._create_terminal_test_info_output_string(
            test, descriptive_test_name)
        test.set_test_id_string(terminal_output_string)

        # Modelsim runner create a run.do file to run simulation.
        self._write_run_do_file(test=test,
                                generic_call=gen_call,
                                module_call=module_call)

        # Call Simulate in sub-class
        sim_success = self._simulate(test=test, generic_call=gen_call,
                                     module_call=module_call)

        # Check simulation output
        self._check_test_result(test=test, sim_start_time=sim_start_time, sim_success=sim_success)

        # Update test register
        test.set_folder_to_name_mapping(descriptive_test_name)

    def _write_run_do_file(self, test, generic_call, module_call):
        '''
        Overload in sub-class, not valid for GHDLRunner.
        '''
        pass

    @staticmethod
    def _create_test_folder(path) -> None:
        '''
        Create the test folder for this test run.
        '''
        try:
            os.makedirs(path, exist_ok=True)
        except:
            raise TestOutputPathError(path)

    def _read_transcript_file(self, test_run_path) -> list:
        transcript_file = os.path.join(test_run_path, 'transcript')
        try:
            # Read file content
            with open(transcript_file, 'r') as file:
                lines = file.readlines()
        except FileNotFoundError:
            self.logger.error('File not found: %s' % (transcript_file))
            lines = None
        return lines

    def _check_test_result(self, test, sim_start_time, sim_success) -> None:
        '''
        Check test run transcript file for passing/failing test.
        Add passing/failing test to test lists and present to transcript.
        '''
        if not self.project.settings.get_result_check_str():
            self.logger.debug("Checking for UVVM summary report")
        else:
            self.logger.debug("Checking for %s." %
                              (self.project.settings.get_result_check_str()))

        lines = self._read_transcript_file(test.get_test_path())

        # Check file content
        summary_found = False
        test_ok = False
        test_ok_no_minor_alerts = True
        if lines is not None:
            for line in lines:
                # Use default: UVVM summary
                if not self.project.settings.get_result_check_str():
                    # Locate UVVM summary start
                    if re.search(self.RE_UVVM_SUMMARY, line) and not summary_found:
                        summary_found = True
                    # Locate UVVM simulation PASS line - after finding UVVM summary start
                    if re.search(self.RE_UVVM_RESULT_ALL_PASS, line) and summary_found:
                        test_ok = True
                        # Check if minor alerts have been triggered
                        if re.search(self.RE_UVVM_RESULT_PASS_WITH_MINOR, line):
                            test_ok_no_minor_alerts = False
                        break

                # Use user selected result checking string
                else:
                    if re.search(self.RE_USER, line):
                        test_ok = True
                        break

        # Fail if the simulation was not determined as successfull, regardless if we found other info in the transcript
        test_ok = test_ok and sim_success

        # Calculate timing
        sim_end_time = round(time.time() * 1000)
        elapsed_time = sim_end_time-sim_start_time
        sim_sec, sim_min, sim_hrs = convert_from_millisec(elapsed_time)

        # Set test result
        if test_ok is True:
            test_str_result = self.logger.green()+'PASS'
            if test_ok_no_minor_alerts is False:
                test_str_result += self.logger.yellow()+' (with minor alerts)'
        else:
            test_str_result = self.logger.red()+'FAIL'
        test_str_result += self.logger.reset_color()

        test_details_str = '%s%s (%dh:%dm:%ds).\n' % (test.get_terminal_test_string(),
                                                      test_str_result,
                                                      sim_hrs,
                                                      sim_min,
                                                      sim_sec)

        # Save 30 final lines if there was an error in the simulations
        if (test_ok is False) and (lines is not None):
            test.set_test_error_summary(lines)

        test.set_terminal_test_details_str(test_details_str)
        test.set_result_success(
            test_ok, no_minor_alerts=test_ok_no_minor_alerts)

    @staticmethod
    def _create_terminal_test_info_output_string(test, descriptive_test_name) -> str:
        '''
        Create a testcase name based on entity, architecture, test and generics.
        '''
        test_string = 'Running: '
        # Build string base for test run result reporting
        generics = test.get_gc_str()
        if generics:
            generics = generics.replace('-g', '')
        test_string += descriptive_test_name.replace('(', '.').replace(')', '')

        testcase = test.get_tc()
        if testcase:
            test_string += '.' + testcase
        if generics:
            test_string += '\nGenerics: ' + generics
        if test.get_netlist_timing():
            test_string += '\nTiming: ' + test.get_netlist_timing()
        test_string += '\nResult: '
        return test_string
