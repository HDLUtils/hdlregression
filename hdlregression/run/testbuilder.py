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

import fnmatch

from ..construct.container import Container
from ..report.logger import Logger
from ..construct.hdlfile import VHDLFile, VerilogFile
from .hdltests import VHDLTest, VerilogTest


class TestBuilder:
    '''
    Builds list of tests that will be run.
    Test list entries are:
    (testbench (object), testcase (string))
    '''

    def __init__(self, project):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        self.testbench_container = Container(name=__name__)
        self.test_container = Container(name='test_container')
        self.base_tests_container = Container(name='base_tests_container')
        self.run_tests = []

    def build_tb_module_list(self) -> None:
        '''
        Builds a list of all TB modules.
        '''
        library_list = self.project._get_library_container().get()
        for library in library_list:
            for hdlfile in library.get_hdlfile_list():
                self.logger.debug("checking for TB in %s in library %s" % (hdlfile.get_name(),
                                                                           library.get_name()))
                for module in hdlfile.get_tb_modules():
                    self.testbench_container.add(module)

    def build_list_of_tests_to_run(self):
        '''
        Builds a list of all testbenches and testcases
        that are selected to be run.
        '''
        # Build all possible tests as starting point
        self._build_base_tests()

        # Run all
        if self.project.settings.get_run_all():
            self.logger.debug("building tests for full regression")

        # Run in GUI mode
        elif self.project.settings.get_gui_mode():
            self.logger.debug("building tests for gui mode")

            if self.project.settings.get_testcase():
                self._build_testcase()
            elif self.project.settings.get_testgroup():
                self._build_testgroup()
            else:
                self._build_modified()

            if self._get_num_tests_to_run() == 0:
                self._set_return_code(1)

        # Run testcase
        elif self.project.settings.get_testcase():
            self.logger.debug("building tests for testcase")
            self._build_testcase()
            if self._get_num_tests_to_run() == 0:
                self._set_return_code(1)
        # Run testgroup
        elif self.project.settings.get_testgroup():
            self.logger.debug("building tests for testgroup")
            self._build_testgroup()
            if self._get_num_tests_to_run() == 0:
                self._set_return_code(1)
        # Run only changed
        else:
            self.logger.debug("building tests for changed only")
            self._build_modified()

    def get_list_of_tests_to_run(self) -> list:
        '''
        Returns list of all testbenches and testcases
        that are selected to be run.
        '''
        return self.test_container.get()

    def get_num_tests_run(self) -> int:
        return len(self.run_tests)

    def get_num_tests(self) -> int:
        return len(self.base_tests_container.get())

    # ====================================================================
    # Test builder methods
    # ====================================================================

    def _get_num_tests_to_run(self) -> int:
        return self.test_container.num_elements()

    def _set_return_code(self, return_code):
        self.project.settings.set_return_code(return_code)

    def _str_match(self, str1, str2) -> bool:
        return str1.upper() == str2.upper()

    def _build_base_tests(self) -> None:
        '''
        Build a list of all tests.
        '''
        # Remove any existing test(s)
        self.test_container.empty_list()
        self.base_tests_container.empty_list()

        sequencer_testcase_string = self.project.settings.get_testcase_identifier_name()

        # Iterate all TBs
        for tb in self.testbench_container.get():

            # Locate generic container for this TB, i.e.
            # generics set by test script designer.
            gc_list_all = []
            for gc in self.project.generic_container.get():
                if self._str_match(gc.get_name(), tb.get_name()):
                    gc_list_all = gc.get()

            # ------------------------------------
            # Verilog TB
            # ------------------------------------
            if tb.get_hdlfile().check_file_type('verilog'):
                tc_gc_set = False
                for gc in gc_list_all:
                    for gc_item in gc:
                        if isinstance(gc_item, str):
                            if self._str_match(gc_item, sequencer_testcase_string):
                                tc_gc_set = True

                # Scripted generics tests
                if gc_list_all:
                    # Create tests with all sequencer built-in testcases?
                    if tc_gc_set is False and tb.get_has_testcase():
                        for tc in tb.get_testcase():
                            for gc in gc_list_all:
                                test = self._get_test_object(tb=tb)
                                test.set_gc(gc)
                                test.set_tc(tc)
                                self.test_container.add(test)
                # No scripted generics tests
                else:
                    # Tests from detected sequencer testcases
                    for tc in tb.get_testcase():
                        test = self._get_test_object(tb=tb)
                        test.set_tc(tc)
                        self.test_container.add(test)

            # ------------------------------------
            # VHDL TB
            # ------------------------------------
            else:
                # Generics for non-specified architecture, i.e. all architectures
                gc_list_no_arch = [
                    gc for (gc_arch, gc) in gc_list_all if gc_arch is None]

                # Match with architecture
                for arch in tb.get_architecture():

                    # Script generics set for this architecture
                    gc_list_this_arch = [gc for (
                        gc_arch, gc) in gc_list_all if gc_arch is not None if self._str_match(gc_arch, arch.get_name())]

                    # Combined generics list with generics set without
                    # architecture and generics set for this architecture
                    gc_list_combined = (gc_list_this_arch + gc_list_no_arch)

                    tc_gc_set = False
                    for gc in gc_list_combined:
                        for gc_item in gc:
                            if isinstance(gc_item, str):
                                if self._str_match(gc_item, sequencer_testcase_string):
                                    tc_gc_set = True

                    # Scripted generics tests
                    if gc_list_combined:

                        # Create tests with all sequencer built-in testcases?
                        if tc_gc_set is False and arch.get_has_testcase():
                            for tc in arch.get_testcase():
                                for gc in gc_list_combined:
                                    test = self._get_test_object(tb=tb)
                                    test.set_arch(arch)
                                    test.set_gc(gc)
                                    test.set_tc(tc)
                                    self.test_container.add(test)

                        # Or, user has selected sequencer built-in testcase
                        else:
                            for gc in gc_list_combined:
                                test = self._get_test_object(tb=tb)
                                test.set_arch(arch)

                                if self._str_match(gc[0], sequencer_testcase_string):
                                    test.set_tc(gc[1])
                                else:
                                    test.set_gc(gc)

                                self.test_container.add(test)

                    # No scripted generics tests
                    else:
                        # Test without generics
                        test = self._get_test_object(tb=tb)

                        # Check if test has GC_TESTCASE setting
                        if arch.get_has_testcase() is False:
                            test.set_arch(arch)
                            self.test_container.add(test)
                        else:
                            # Tests from detected sequencer testcases
                            for tc in arch.get_testcase():
                                test = self._get_test_object(tb=tb)
                                test.set_arch(arch)
                                test.set_tc(tc)
                                self.test_container.add(test)

        self.base_tests_container.add_element_from_list(
            self.test_container.get())

    @staticmethod
    def _unix_match(search_string, pattern) -> bool:
        '''
        Match search_string with pattern using Unix wild cards.
        '''
        return fnmatch.fnmatch(search_string, pattern)

    def _get_user_testcase_list(self) -> list:
        return self.project.settings.get_testcase_list()

    def _build_testcase(self) -> None:
        '''
        Build a list of tests that match
        user selected testcase.
        '''

        def _is_testcase_an_index_number():
            return all(tc[0].isdigit() for tc in testcase_list)

        def _get_testcase_index_number() -> int:
            testcase_index = int(testcase_list[0][0])
            if testcase_index >= 1:
                # return testcase listed number as listed in termial.
                return testcase_index - 1
            else:
                return None

        # Get user seleceted testcase
        testcase_list = self._get_user_testcase_list()

        # Select based on user input as number og testcase name
        if _is_testcase_an_index_number() is True:
            index = _get_testcase_index_number()
            self._get_testcase_from_index(index)
        else:
            self._get_testcase_from_string(testcase_list)

        # Verify if any testcases were found
        if self.test_container.num_elements() == 0:
            for testcase in testcase_list:
                self.logger.warning('No testcase match for: %s' % (testcase))

    def _get_testcase_from_index(self, index):
        ''' User selected testcase by number. '''
        test = self.test_container.get_index(index)
        self.test_container.empty_list()
        self.test_container.add(test)

    def _get_testcase_from_string(self, testcase_list):
        ''' User selected testcase ny entity.arch.tc '''
        filtered_tests = []

        for test in self.test_container.get():

            for tc in testcase_list:
                # User selection content
                user_testbench = tc[0]
                user_architecture = tc[1]
                user_testcase = tc[2]

                # Test container test content
                container_testbench = test.get_name()
                container_architecture = test.get_arch().get_name()
                container_testcase = test.get_tc()

                # Locate correct testbench
                if self._unix_match(search_string=container_testbench, pattern=user_testbench):
                    # Locate correct architecture
                    if user_architecture:
                        if self._unix_match(search_string=container_architecture, pattern=user_architecture):

                            # Selected sequencer/built-in testcase?
                            if container_testcase:
                                # User selected testcase?
                                if user_testcase:
                                    if self._unix_match(search_string=container_testcase, pattern=user_testcase):
                                        filtered_tests.append(test)
                                else:
                                    filtered_tests.append(test)
                            else:
                                filtered_tests.append(test)

                    # All architectures
                    else:
                        # Selected sequencer/built-in testcase?
                        if container_testcase:
                            if user_testcase:
                                if self._unix_match(search_string=container_testcase, pattern=user_testcase):
                                    filtered_tests.append(test)
                            # All sequencer/built-in testcases
                            else:
                                filtered_tests.append(test)
                        else:
                            filtered_tests.append(test)

        self.test_container.empty_list()
        for test in filtered_tests:
            self.test_container.add(test)

    def _build_testgroup(self) -> None:
        '''
        Build a list of tests that are
        part of testgroup.
        '''
        filtered_tests = []

        # Get which testgroup to run.
        testgroup_to_run = self.project.settings.get_testgroup()

        # Get testgroup info
        testgroup = self.project._get_testgroup_container(testgroup_name=testgroup_to_run,
                                                          create_if_not_found=False)

        if testgroup:
            # Locate all tests in test group
            for test_run in testgroup.get():
                # Extract test parts
                (entity, architecture, testcase, generics) = test_run

                # Check for match with test container (base tests)
                for test in self.test_container.get():

                    # Match entity
                    if self._unix_match(search_string=test.get_name(), pattern=entity):

                        # Match architecture
                        if architecture:
                            if self._unix_match(search_string=test.get_arch().get_name(), pattern=architecture):

                                # User selected sequencer testcase?
                                if testcase:
                                    # Match sequencer testcase
                                    if self._unix_match(search_string=test.get_tc(), pattern=testcase):
                                        filtered_tests.append(test)
                                else:
                                    filtered_tests.append(test)
                        else:
                            filtered_tests.append(test)

        self.test_container.empty_list()
        for test in filtered_tests:
            self.test_container.add(test)

        if self.test_container.num_elements() == 0:
            self.logger.warning(
                'No test found for test group: %s' % (testgroup_to_run))

    def _build_modified(self) -> None:
        '''
        Build a list of tests that have to
        be re-run due to changes.
        '''
        filtered_tests = []
        for test in self.test_container.get():

            if test.get_need_to_simulate() is True:
                filtered_tests.append(test)
            elif not self.project.settings.get_success_run():
                filtered_tests.append(test)

        self.test_container.empty_list()
        for test in filtered_tests:
            self.test_container.add(test)

    def _get_test_object(self, tb=None, arch=None, tc=None, gc=None):
        '''
        Will return test object based on HDL file type.
        '''
        hdlfile = tb.get_hdlfile()
        if isinstance(hdlfile, VHDLFile):
            test = VHDLTest(tb=tb, arch=arch, tc=tc, gc=gc,
                            settings=self.project.settings)
            test.set_hdlfile(hdlfile)
            test.set_need_to_simulate(hdlfile.get_need_compile())
            return test
        elif isinstance(hdlfile, VerilogFile):
            test = VerilogTest(tb=tb, settings=self.project.settings)
            test.set_hdlfile(hdlfile)
            test.set_need_to_simulate(hdlfile.get_need_compile())
            return test
        else:
            self.logger.warning('Filetype not detected for %s' %
                                (type(tb.get_hdlfile())))
            return None
