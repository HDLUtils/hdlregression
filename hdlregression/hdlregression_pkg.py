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

import platform
import os
import shutil
from glob import glob
from multiprocessing.pool import ThreadPool

from .settings import HDLRegressionSettings
from .report.logger import Logger
from pickle import FALSE


def dict_keys_to_lower(dictionary) -> dict:
    '''
    Convert dictionary keys to lower case
    '''
    dictionary = dict((k.lower(), v) for k, v in dictionary.items())
    return dictionary

# ====================================================================
# Listing methods
# ====================================================================


def list_compile_order(container) -> str:
    '''
    List libraries with belonging files in compile order.

    Returns:
    comp_order_str(str): a string with compile order for project.
    '''
    comp_order_str = f"\n{'='*20} Compile Order For Project {'='*20}\n"

    for idx, library in enumerate(container.get()):
        compile = "(recompile)" if library.get_need_compile() else ""
        if any(lib for lib in library.get_lib_obj_dep() if lib.get_need_compile()):
            compile = "(recompile)"
        comp_order_str += f"|--[{idx+1}]-- {library.get_name()} {compile}\n"

        for hdlfile in library.get_compile_order_list():
            tb = "(TB)" if hdlfile.get_is_tb() else ""
            rc = "(rc)" if hdlfile.get_need_compile() else ""
            comp_order_str += f"|      |--  {hdlfile.get_name()} {tb} {rc}\n"

    comp_order_str += "\n"
    return comp_order_str


def list_testgroup(container) -> str:
    '''
    List all testgroups with belonging testbenches/testcases.

    Returns:
    tg_str(str): a string with all testgroups.
    '''
    tg_str = ""

    for testgroup_container in container.get():
        tg_str += f"|---- {testgroup_container.get_name()}\n"

        testgroup_items_list = testgroup_container.get()
        for testgroup_items_list in testgroup_container.get():
            entity, architecture, testcase, generics = tuple(
                testgroup_items_list)

            tg_str += "|   |--  %s" % (entity)
            if architecture:
                tg_str += ".%s" % (architecture)
            if testcase:
                tg_str += ".%s" % (testcase)
            if generics:
                tg_str += ", generics=%s" % (generics)
            tg_str += '\n'

    if not tg_str:
        return 'No test group found.'
    return tg_str


def list_testcases(runner) -> str:
    '''
    List all testcases discovered inside testbenches.

    Returns:
    tc_string: a string of all discovered testcases in project.
    '''
    tc_string = ""

    runner.testbuilder.build_tb_module_list()
    runner.testbuilder._build_base_tests()
    run_tests = runner.testbuilder.test_container.get()

    for test in run_tests:
        generics = test.get_gc_str(filter_testcase_id=True).replace('-g', '') if test.get_gc_str() else ''

        tc_string += 'TC:%d - %s\n' % (test.get_test_id_number(),
                                       test.get_testcase_name())
        if generics:
            tc_string += '    Generics: %s\n' % (generics)

    return tc_string

# ========================================================
#
# Helper class and methods
#
# ========================================================


def os_adjust_path(path) -> str:
    if platform.system().lower() == "windows":
        return path.replace('\\', '//')
    else:
        return path.replace('\\', '\\\\')


def simulator_detector() -> list:
    '''
    Method will be used for getting a modelsim.ini file
    '''
    detected_simulators = []
    path_env = os.environ['PATH']
    if 'ghdl' in path_env.lower():
        detected_simulators.append('GHDL')
    if 'nvc' in path_env.lower():
        detected_simulators.append('NVC')
    if 'modelsim' in path_env.lower():
        detected_simulators.append('MODELSIM')
    if 'aldec' in path_env.lower():
        detected_simulators.append('ALDEC')

    return detected_simulators


def adjust_generic_value_paths(generic_list, settings, logger) -> list:
    '''
    Check generic values if they are marked as PATH and pad
    paths with user script path information.
    '''

    # Helper methods
    def check_if_generic_value_is_path(generic_data) -> bool:
        if isinstance(generic_data, str):
            return False
        elif isinstance(generic_data, tuple):
            if len(generic_data) != 2:
                logger.warning('Add generic value as tuple require 2 items.')
                return False
            else:
                if generic_data[1].upper() == 'PATH':
                    return True
        return False

    def pad_generic_path_value(generic_value) -> str:
        return os_adjust_path(os.path.join(settings.get_script_path(), generic_value))

    return_list = []
    for idx, data in enumerate(generic_list):
        if idx % 2 == 0:
            generic_name = data
        else:
            generic_data = data
            if check_if_generic_value_is_path(generic_data):
                generic_data = pad_generic_path_value(generic_data[0])
            return_list += [generic_name, generic_data]
    return return_list


def convert_from_millisec(millis):
    seconds = (millis / 1000) % 60
    minutes = (millis / (1000 * 60)) % 60
    hours = (millis / (1000 * 60 * 60)) % 24
    return int(seconds), int(minutes), int(hours)


def validate_testgroup_parameters(testgroup_name: str,
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


def validate_cached_version(project,
                            installed_version: str) -> bool:
    '''
    Compare installed version with cache version.

    :rtype: bool
    :return: True if cached version matches installed version.
    '''
    # Load cached HDLRegression version number
    cached_version = project.settings.get_hdlregression_version()
    # Compare current version with cached version
    if (cached_version != installed_version) and (cached_version != '0.0.0'):
        project.logger.warning('WARNING! HDLRegression v%s not compatible with cached v%s. '
                               'Executing database rebuild.' % 
                               (installed_version, cached_version))
        return False
    return True


def print_info_msg_when_no_test_has_run(project, runner):
    ''' Display info message if no tests have been run. '''
    if runner.get_num_tests() == 0:
        project.logger.info('\nNo tests found.')
        project.logger.info(
            'Ensure that the "--hdlregression:tb" (VHDL) / "//hdlregression:tb"'
            ' (Verilog) pragma is set in the testbench file(s).')
    elif project.get_num_tests_run() == 0:
        project.logger.info(
            'Test run not required. Use "-fr"/"--fullRegression" to re-run all tests.')


def display_info_text(version) -> None:
    ''' Presents HDLRegression version number and QR info. '''
    print('''
%s
  HDLRegression version %s
  See /doc/hdlregression.pdf for documentation.
%s

''' % ('=' * 70, version, '=' * 70))


def print_run_success(project):
    if project.settings.get_return_code() == 0:
        project.logger.info('SIMULATION SUCCESS: %d passing test(s).'
                            % (project.get_num_pass_tests()), color='green')
        num_minor_alerts = project.get_num_pass_with_minor_alert_tests()
        if num_minor_alerts > 0:
            project.logger.warning(
                '%d test(s) passed with minor alert(s).'
                % (num_minor_alerts))
    else:
        project.logger.warning('SIMULATION FAIL: %d tests run, %d test(s) failed.'
                               % (project.get_num_tests_run(),
                                  project.get_num_fail_tests()))


def clean_generated_output(project, restore_settings=False):
    saved_settings = project.settings
    project.settings.set_clean(True)
    project._rebuild_databases_if_required_or_requested(False)
    if restore_settings is True:
        project.settings = saved_settings


def empty_project_folder(project):
    # Clean output, i.e. delete all
    if os.path.isdir(project.settings.get_output_path()):
        shutil.rmtree(project.settings.get_output_path())
        project.logger.info('Project output path %s cleaned.' % 
                            (project.settings.get_output_path()))
        try:
            os.mkdir(project.settings.get_output_path())
        except OSError as error:
            project.logger.error(
                'Unable to create output folder, %s.' % (error))
    else:
        project.logger.info('No output folder to delete: %s.' % 
                            (project.settings.get_output_path()))


def disable_threading(project):
    ''' Disable threading so the next run will start as normal. '''
    project.settings.set_threading(False)
    project.settings.set_num_threads(1)


def run_from_gui(project) -> bool:
    if project.settings.get_gui_mode():
        return project.settings.get_simulator_name() == "MODELSIM"
    else:
        return False


def update_settings_from_arguments(project,
                                   kwargs: dict):
    '''
    Adjust the run settings with scripted run arguments
    passed on with the start() call.

    :param kwargs: Keyword arguments
    :type kwargs: dict
    '''

    # Update if GUI mode is selected without overriding terminal argument
    if not project.settings.get_gui_mode():
        if 'gui_mode' in kwargs:
            project.settings.set_gui_mode(kwargs.get('gui_mode'))

    # Set what to do if a testcase fails.
    if not project.settings.get_stop_on_failure():
        if 'stop_on_failure' in kwargs:
            project.settings.set_stop_on_failure(
                kwargs.get('stop_on_failure'))

    # Regression_mode: only run new and changed code
    if project.settings.get_run_all() is True:  # CLI argument
        project.settings.set_run_all(True)
    elif 'regression_mode' in kwargs:  # API argument
        project.settings.set_run_all(kwargs.get('regression_mode'))
    else:  # default
        project.settings.set_run_all(False)

    # Enable multi-threading
    if 'threading' in kwargs:
        project.logger.info('Threading active.')
        project.settings.set_threading(kwargs.get('threading'))
    # Verbosity
    if 'verbose' in kwargs:
        project.settings.set_verbose(True)
    # Simulation options
    if 'sim_options' in kwargs:
        project.settings.set_sim_options(kwargs.get('sim_options'))
    if 'netlist_timing' in kwargs:
        project.settings.set_netlist_timing(kwargs.get('netlist_timing'))

    # Coverage options
    if 'keep_code_coverage' in kwargs:
        if kwargs.get('keep_code_coverage') is True:
            project.settings.set_keep_code_coverage(keep_code_coverage=True)

    # UVVM specific
    if 'no_default_com_options' in kwargs:
        if kwargs.get('no_default_com_options') is True:
            # Check if running with defaults
            if project.settings.get_is_default_com_options() is True:
                project.settings.remove_com_options()

    if 'ignore_simulator_exit_codes' in kwargs:
        exit_codes = kwargs.get('ignore_simulator_exit_codes')
        if isinstance(exit_codes, list) is False:
            project.logger.warning('ignore_simulator_exit_codes is not list.')
        else:
            project.settings.set_ignored_simulator_exit_codes(exit_codes)


def request_libraries_prepare(project) -> None:
    ''' Invoke all Library Objects to prepare for compile/simulate. '''

    # Thread method
    def library_prepare(library) -> None:
        library.update_file_list()
        library.check_library_files_for_changes()
        library.prepare_for_run()

    # Get list of all libraries
    library_list = project.library_container.get()
    # Default number of threads
    num_threads = 1
    # Check if threading is enabled, i.e. > 0
    if project.settings.get_num_threads() > 0:
        if len(library_list) > 0:
            num_threads = len(library_list)

    # Execute using 1 or more threads
    with ThreadPool(num_threads) as pool:
        pool.map(library_prepare, library_list)


def organize_libraries_by_dependency(project) -> None:
    """
    Organize libraries by dependency order.

    :rtype: bool
    :return: Status of setting up library dependencies.
    """
    # Skip if no libraries have changes.
    lib_changes = any(lib.get_need_compile()
                      for lib in project.library_container.get())
    if lib_changes is False:
        return True

    # Organize by dependency - this value of i corresponds to
    # how many values were sorted.
    num_libraries = project.library_container.num_elements()
    libraries = project.library_container.get()

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
                        project.logger.error('Recursive library dependency: %s and %s.' % (
                            check_lib.get_name(), with_lib.get_name()))
                        continue
                    lowest_value_index = j
            # Swap values of the lowest unsorted element with the
            # first unsorted element.
            if i != lowest_value_index:
                project.logger.debug(
                    f"Swapping: {check_lib.get_name()} <-> {with_lib.get_name()}.")
                (libraries[i], libraries[lowest_value_index]) = \
                    (libraries[lowest_value_index], libraries[i])
                swapped = True
    return True


def validate_path(project, path=None, filename=None) -> bool:
    file_or_path_to_check = path if path is not None else filename
    if file_or_path_to_check is not None and glob(file_or_path_to_check):
        return True
    else:
        print_invalid_path_warning(project, file_or_path_to_check)
        return False


def check_file_exist(filename) -> bool:
    if glob(filename):
        return True
    else:
        return False


def print_invalid_path_warning(project, path):
    project.logger.warning('Path or file not found: %s\n'
                           ' -> In Python strings, the backslash "\\" is a special character, also called the "escape" character.\n'
                           '    Use forwardslash "/", double backslash "\\\\" or raw text string r"path".' % (path))


def compile_uvvm_all(project, path) -> bool:
    '''
    Locate uvvm/script/component_list.txt
    Inside each verification component: locate <comp>/script/compile_order.txt and run add_files()
    '''
    uvvm_path = path
    if os.path.isdir(uvvm_path) is False:
        project.logger.error(f'Path to UVVM is incorrect: {uvvm_path}')
        return False
    uvvm_component_script = os.path.join(uvvm_path, 'script', 'component_list.txt')
    if os.path.isfile(uvvm_component_script) is False:
        project.logger.error(f'UVVM component_list.txt not found: {uvvm_component_script}')
        return False
    
    with open(uvvm_component_script, 'r') as component_file:
        component_list = component_file.readlines()
        
    uvvm_components = [component.strip() for component in component_list]
    
    for component in uvvm_components:
        script_path = os.path.join(uvvm_path, component, 'script')
        compile_order_file = os.path.join(script_path, 'compile_order.txt')
        if os.path.isfile(compile_order_file) is False:
            project.logger.warning(f'UVVM compile_order.txt not found for: {component.strip()}')
        else:
            with open(compile_order_file, 'r') as f:
                lines = f.readlines()
            
            # filter out library line at the beginning
            src_file_list = [line.strip() for line in lines if not '#' in line and line.isspace() is False]
       
            # Convert to absolute paths and add to add_file()
            for line in src_file_list:
                file_path = os.path.join(script_path, line)
                project.add_files(os_adjust_path(file_path), library_name=component)
                    
    return True
