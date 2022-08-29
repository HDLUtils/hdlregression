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
import zlib


class HdlRegressionTest:

    def __init__(self, tb=None, settings=None):
        self.result = 'NA'
        self.path = None
        self.tb = None
        self.result_success = False
        self.no_minor_alerts = False
        self.test_mapping_name = None
        self.test_index = 0
        self.test_string = None
        self.settings = settings
        self.id_number = 0
        self.terminal_test_details_str = None
        self.test_error_summary = None
        self.terminal_test_string = None

        self.hdlfile = None
        self.test_output = []
        self.need_to_simulate = False

        self.set_tb(tb)

        self.netlist_timing = None

    def clear_output(self) -> None:
        '''
        Clears stored sim output from test run.
        '''
        self.test_output = []

    def add_output(self, output_lines) -> None:
        """
        Save test output so it can be printed to terminal in verbose mode.
        """
        self.test_output.append(output_lines)

    def get_output(self) -> str:
        '''
        Returns sim output from test run.
        '''
        return "\n".join(self.test_output)

    def set_test_error_summary(self, output_lines) -> None:
        """
        A section of the test output is saved so that the
        test error can be printed from a failing testcase.
        """
        error_lines = ''.join(output_lines[len(output_lines)-30:])
        self.test_error_summary = '\n%s\n%s\n%s\n' % (('===='*40),
                                                      ''.join(error_lines),
                                                      ('===='*40))

    def get_test_error_summary(self) -> str:
        return self.test_error_summary

    def set_terminal_test_details_str(self, test_details) -> None:
        self.terminal_test_details_str = test_details

    def get_terminal_test_details_str(self) -> str:
        return self.terminal_test_details_str

    def set_terminal_test_string(self, test_string) -> None:
        self.terminal_test_string = test_string

    def get_terminal_test_string(self) -> str:
        return self.terminal_test_string

    def set_test_id_string(self, test_string):
        '''
        Testcase name as represented in terminal,
        used for test register, i.e. statistic methods.
        Set by SimRunner() when run in terminal mode.
        '''
        # Save original test string before editing.
        self.set_terminal_test_string(test_string)

        # remove leading "Running: " and new line from test_string
        test_string = test_string[test_string.find(':')+1:].strip()
        # remove auxiliary "\nGENERICS" from test_string
        if '\n' in test_string:
            test_string = test_string[:test_string.index('\n')]
        # save
        self.test_string = test_string

    def get_test_id_string(self) -> str:
        '''
        Testcase name as represented in terminal,
        used for test register, i.e. statistic methods.
        '''
        return self.test_string

    def set_hdlfile(self, hdlfile):
        self.hdlfile = hdlfile

    def get_hdlfile(self):
        return self.hdlfile

    def set_need_to_simulate(self, need_to_simulate:bool=False):
        self.need_to_simulate = need_to_simulate

    def get_need_to_simulate(self) -> bool:
        return self.need_to_simulate

    def set_index(self, index):
        self.test_index = index

    def get_index(self) -> int:
        return self.test_index

    def set_result(self, result) -> None:
        self.result = result

    def get_result(self) -> str:
        return self.result

    def set_result_success(self, success, no_minor_alerts=True):
        self.result_success = success
        self.no_minor_alerts = no_minor_alerts

    def get_result_success(self) -> bool:
        return self.result_success

    def get_no_minor_alerts(self) -> bool:
        return self.no_minor_alerts

    def set_tb(self, tb) -> None:
        self.tb = tb

    def get_tb(self):
        return self.tb

    def get_library(self):
        pass

    def get_is_vhdl(self) -> bool:
        return False

    def get_is_verilog(self) -> bool:
        return False

    def get_gc_str(self) -> str:
        return ''

    def get_name(self) -> str:
        if self.tb:
            return self.tb.get_name()
        else:
            return 'UNKNOWN'

    def get_arch(self):
        pass

    def get_tc(self):
        pass

    def set_tc(self, tc) -> None:
        pass

    def set_folder_to_name_mapping(self, name):
        self.test_mapping_name = name

    def get_folder_to_name_mapping(self) -> str:
        test_map_name = self.test_mapping_name
        if self.get_gc_str():
            test_map_name += ':' + self.get_gc_str().replace('-g', '')

        map_string = self.get_test_output_folder() + ', ' + test_map_name + '\n'
        return map_string

    def get_test_path(self) -> str:
        path = os.path.join(self.settings.get_test_path(),
                            self.get_tb().get_name())
        if self.get_is_vhdl():
            # Generate unique name for the test run
            test_base_path = path
            gc_str = self.get_gc_str()
            tb_arch_name = self.get_arch().get_name()

            test_folder = zlib.adler32((tb_arch_name + gc_str).encode())
            path = os.path.join(test_base_path, str(test_folder))

        return path

    def get_test_base_path(self) -> str:
        return os.path.join(self.settings.get_test_path(), self.get_tb().get_name())

    def get_test_output_folder(self) -> str:
        '''
        Create a test folder for this test run and return folder name.
        '''
        if self.get_is_vhdl():
            # Generate unique name for the test run
            test_base_path = self.get_test_base_path()
            gc_str = self.get_gc_str()
            tb_arch_name = self.get_arch().get_name()

            test_folder = zlib.adler32((tb_arch_name + gc_str).encode())
            path = os.path.join(test_base_path, str(test_folder))
        else:
            path = self.get_test_base_path()

        return path

    def set_test_id_number(self, number):
        self.id_number = number

    def get_test_id_number(self) -> int:
        return self.id_number

    def get_testcase_name(self) -> str:
        pass

    def get_sim_options(self) -> str:
        return self.settings.get_sim_options()

    def set_netlist_timing(self, timing):
        self.netlist_timing = timing

    def get_netlist_timing(self) -> str:
        return self.netlist_timing


class VHDLTest(HdlRegressionTest):

    def __init__(self, tb=None, arch=None, tc=None, gc=[], settings=None):
        super().__init__(tb=tb, settings=settings)
        self.arch = None
        self.tc = None
        self.gc = None

        self.set_arch(arch)
        self.set_tc(tc)
        self.set_gc(gc)
        self.set_netlist_timing(settings.get_netlist_timing())

    def get_is_vhdl(self) -> bool:
        return True

    def get_library(self):
        return self.get_tb().get_library()

    def set_arch(self, arch) -> None:
        self.arch = arch

    def get_arch(self) -> str:
        return self.arch

    def set_tc(self, tc) -> None:
        self.tc = tc

    def get_tc(self) -> str:
        return self.tc

    def set_gc(self, gc) -> None:
        if isinstance(gc, list):
            self.gc = gc

    def get_gc(self) -> list:
        return self.gc

    def get_gc_str(self) -> str:
        ID_TESTCASE = self.settings.get_testcase_identifier_name().upper()

        tb = self.get_tb()

        # Get list of generics that were discovered in this TB
        tb_disc_gc_list = [gc.upper() for gc in tb.get_generic()]

        # Init the generic call with testcase if applicable
        tc = self.get_tc()
        gc_str = '-g'+ID_TESTCASE+'='+tc if tc else ""

        generic_list = self.get_gc()

        if generic_list is None:
            return gc_str

        generic_name = ""
        for idx, gc_item in enumerate(generic_list):
            if idx % 2 == 0:
                generic_name = gc_item.upper()
            else:
                generic_value = str(gc_item)

                # Filter out any non-valid generics
                if generic_name in tb_disc_gc_list:
                    if not gc_str:
                        gc_str = '-g' + generic_name + '=' + generic_value
                    else:
                        gc_str += ' -g' + generic_name + '=' + generic_value

        return gc_str

    def get_testcase_name(self) -> str:
        testcase_name = self.get_name()
        testcase_name += '.' + self.get_arch().get_name()

        if self.get_tc() is not None:
            testcase_name += '.' + self.get_tc()
        return testcase_name


class VerilogTest(HdlRegressionTest):

    def __init__(self, tb=None, tc=None, gc=[], settings=None):
        super().__init__(tb=tb, settings=settings)
        self.tc = None
        self.gc = None
        self.set_tc(tc)
        self.set_gc(gc)
        self.set_netlist_timing(settings.get_netlist_timing())

    def get_is_verilog(self) -> bool:
        return True

    def get_library(self):
        return self.get_tb().get_hdlfile().get_library()

    def get_testcase_name(self) -> str:
        testcase_name = self.get_name()

        return testcase_name

    def set_tc(self, tc) -> None:
        self.tc = tc

    def get_tc(self) -> str:
        return self.tc

    def set_gc(self, gc) -> None:
        if isinstance(gc, list):
            self.gc = gc

    def get_gc(self) -> list:
        return self.gc

    def get_gc_str(self) -> str:
        ID_TESTCASE = self.settings.get_testcase_identifier_name().upper()

        tb = self.get_tb()

        # Get list of all parameters that were discovered in this TB
        tb_disc_parameter_list = [
            parameter for parameter in tb.get_parameter()]

        # Init the generic call with testcase if applicable
        tc = self.get_tc()

        gc_str = '-g'+ID_TESTCASE+'='+tc if tc else ""

        generic_list = self.get_gc()

        if generic_list is None:
            return gc_str

        generic_name = ""
        for idx, gc_item in enumerate(generic_list):
            if idx % 2 == 0:
                generic_name = gc_item.upper()
            else:
                generic_value = str(gc_item)

                # Filter out any non-valid generics
                if generic_name in tb_disc_parameter_list:
                    if not gc_str:
                        gc_str = '-g' + generic_name + '=' + generic_value
                    else:
                        gc_str += ' -g' + generic_name + '=' + generic_value

        return gc_str
