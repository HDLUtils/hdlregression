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
from pickle import FALSE

from ..hdlregression_pkg import get_window_width


class TestStatus:
    PASS = "PASS"
    PASS_WITH_MINOR = "PASS_WITH_MINOR"
    FAIL = "FAIL"
    NOT_RUN = "NOT_RUN"
    RE_RUN = "RE_RUN"


class HdlRegressionTest:
    def __init__(self, tb=None, settings=None):
        self.path = None
        self.tb = None
        self.test_mapping_name = None
        self.test_string = None
        self.settings = settings
        self.id_number = 0
        self.terminal_test_details_str = None
        self.test_error_summary = None
        self.terminal_test_string = None

        self.num_sim_errors = 0
        self.num_sim_warnings = 0

        self.test_status = TestStatus.NOT_RUN

        self.hdlfile = None
        self.test_output = []

        self.set_tb(tb)

        self.netlist_timing = None

    def clear_output(self) -> None:
        """
        Clears stored sim output from test run.
        """
        self.test_output = []

    def add_output(self, output_lines) -> None:
        """
        Save test output so it can be printed to terminal in verbose mode.
        Input is one single line.
        """
        self.test_output.append(output_lines)

    def add_output_lines(self, output_lines):
        """
        Save test output so it can be printed to terminal in verbose mode.
        Input is list of lines.
        """
        for line in output_lines:
            self.test_output.append(line)

    def get_output(self) -> str:
        """
        Returns sim output from test run.
        """
        return "\n".join(self.test_output)

    def get_output_no_format(self) -> list:
        return self.test_output

    def get_test_error_summary(self) -> str:
        sep = "=" * get_window_width()
        output_lines = self.test_output
        error_lines = "\n".join(output_lines[len(output_lines) - 30 :])
        test_error_summary = "\n\n{}\n\n{}\n\n{}\n\n".format(sep, error_lines, sep)
        return test_error_summary

    def set_terminal_test_details_str(self, test_details) -> None:
        self.terminal_test_details_str = test_details

    def get_terminal_test_details_str(self) -> str:
        return self.terminal_test_details_str

    def set_terminal_test_string(self, test_string) -> None:
        self.terminal_test_string = test_string

    def get_terminal_test_string(self) -> str:
        return self.terminal_test_string

    def set_test_id_string(self, test_string):
        """
        Testcase name as represented in terminal,
        used for test register, i.e. statistic methods.
        Set by SimRunner() when run in terminal mode.
        """
        # Save original test string before editing.
        self.set_terminal_test_string(test_string)

        # remove leading "Running: " and new line from test_string
        test_string = test_string[test_string.find(":") + 1 :].strip()
        # remove auxiliary "\nGENERICS" from test_string
        if "\n" in test_string:
            test_string = test_string[: test_string.index("\n")]
        # save
        self.test_string = test_string

    def get_test_id_string(self) -> str:
        """
        Testcase name as represented in terminal,
        used for test register, i.e. statistic methods.
        """
        return self.test_string

    def set_hdlfile(self, hdlfile):
        self.hdlfile = hdlfile

    def get_hdlfile(self):
        return self.hdlfile

    # ----------- test status ---------------
    def set_status(self, status: TestStatus):
        self.test_status = status.upper()

    def get_status(self) -> TestStatus:
        return self.test_status

    # -------- test connections ---------------

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

    def get_gc_str(self, filter_testcase_id=False) -> str:
        return ""

    def get_name(self) -> str:
        if self.tb:
            return self.tb.get_name()
        else:
            return "UNKNOWN"

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
            test_map_name += ":" + self.get_gc_str().replace("-g", "")

        test_id_str = str(self.get_id_number())
        map_string = (
            test_id_str + ", " + self.get_test_path() + ", " + test_map_name + "\n"
        )
        return map_string

    def get_test_base_path(self) -> str:
        return os.path.join(self.settings.get_test_path(), self.get_tb().get_name())

    def get_test_path(self) -> str:
        return self.test_output_folder_name

    def create_test_output_folder_name(self):
        """
        Create a test folder for this test run and return folder name.
        """
        test_base_path = self.get_test_base_path()
        if self.get_is_vhdl():
            # Generate unique name for the test run
            gc_str = self.get_gc_str()
            tb_arch_name = self.get_arch().get_name()

            test_folder = tb_arch_name + "_" + str(self.get_id_number())
            self.test_output_folder_name = os.path.join(test_base_path, test_folder)
        else:
            self.test_output_folder_name = test_base_path

    def set_id_number(self, number):
        self.id_number = number

    def get_id_number(self) -> int:
        return self.id_number

    def get_testcase_name(self) -> str:
        pass

    def get_sim_options(self) -> str:
        return self.settings.get_sim_options()

    def set_netlist_timing(self, timing):
        self.netlist_timing = timing

    def get_netlist_timing(self) -> str:
        return self.netlist_timing

    def set_num_sim_warnings(self, num):
        self.num_sim_warnings = num

    def inc_num_sim_warnings(self):
        self.num_sim_warnings += 1

    def get_num_sim_warnings(self) -> int:
        return self.num_sim_warnings

    def set_num_sim_errors(self, num):
        self.num_sim_errors = num

    def inc_num_sim_errors(self):
        self.num_sim_errors += 1

    def get_num_sim_errors(self) -> int:
        return self.num_sim_errors


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

    def get_gc_str(self, filter_testcase_id=False) -> str:
        ID_TESTCASE = self.settings.get_testcase_identifier_name().upper()

        tb = self.get_tb()

        # Get list of generics that were discovered in this TB
        tb_disc_gc_list = [gc.upper() for gc in tb.get_generic()]

        # Init the generic call with testcase if applicable
        tc = self.get_tc()
        gc_str = (
            "-g" + ID_TESTCASE + "=" + tc
            if (tc and (filter_testcase_id is False))
            else ""
        )

        generic_list = self.get_gc()

        if generic_list:
            generic_name = ""
            for idx, gc_item in enumerate(generic_list):
                if idx % 2 == 0:
                    generic_name = gc_item.upper()
                else:
                    generic_value = str(gc_item)

                    # Filter out any non-valid generics
                    if generic_name in tb_disc_gc_list:
                        if not gc_str:
                            gc_str = "-g" + generic_name + "=" + generic_value
                        else:
                            gc_str += " -g" + generic_name + "=" + generic_value

        return gc_str

    def get_testcase_name(self) -> str:
        testcase_name = self.get_name()
        testcase_name += "." + self.get_arch().get_name()

        if self.get_tc() is not None:
            testcase_name += "." + self.get_tc()
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

    def get_gc_str(self, filter_testcase_id=False) -> str:
        ID_TESTCASE = self.settings.get_testcase_identifier_name().upper()

        tb = self.get_tb()

        # Get list of all parameters that were discovered in this TB
        tb_disc_parameter_list = [parameter for parameter in tb.get_parameter()]

        # Init the generic call with testcase if applicable
        tc = self.get_tc()

        gc_str = (
            "-g" + ID_TESTCASE + "=" + tc
            if (tc and (filter_testcase_id is False))
            else ""
        )

        generic_list = self.get_gc()

        if generic_list is not None:
            generic_name = ""
            for idx, gc_item in enumerate(generic_list):
                if idx % 2 == 0:
                    generic_name = gc_item.upper()
                else:
                    generic_value = str(gc_item)

                    # Filter out any non-valid generics
                    if generic_name in tb_disc_parameter_list:
                        if not gc_str:
                            gc_str = "-g" + generic_name + "=" + generic_value
                        else:
                            gc_str += " -g" + generic_name + "=" + generic_value

        return gc_str
