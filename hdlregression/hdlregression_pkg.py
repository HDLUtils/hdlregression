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


if __package__ is None or __package__ == '':
    from settings import HDLRegressionSettings
    from logger import Logger
else:
    from .settings import HDLRegressionSettings
    from .report.logger import Logger


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
            entity, architecture, testcase, generics = tuple(testgroup_items_list)

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

    for idx, test in enumerate(run_tests):
        generics = test.get_gc_str().replace('-g', '') if test.get_gc_str() else ''

        tc_string += '%d - %s\n' % (idx + 1, test.get_testcase_name())
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
    seconds = (millis/1000) % 60
    minutes = (millis/(1000*60)) % 60
    hours = (millis/(1000*60*60)) % 24
    return int(seconds), int(minutes), int(hours)

