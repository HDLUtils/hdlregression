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
from .hdltests import VHDLTest, VerilogTest, TestStatus


class TestBuilder:
    """
    Builds list of tests that will be run.
    Test list entries are:
    (testbench (object), testcase (string))
    """

    def __init__(self, project):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        self.testbench_container = Container(name=__name__)
        self.tests_to_run_container = Container(name="tests_to_run_container")
        self.base_tests_container = Container(name="base_tests_container")
        self.test_id_count = 0

    def build_tb_module_list(self) -> None:
        """
        Builds a list of all TB modules.
        """
        library_list = self.project._get_library_container().get()
        for library in library_list:
            for hdlfile in library.get_hdlfile_list():
                self.logger.debug(
                    "checking for TB in %s in library %s"
                    % (hdlfile.get_name(), library.get_name())
                )
                for module in hdlfile.get_tb_modules():
                    self.testbench_container.add(module)

    def build_list_of_tests_to_run(self, re_run_tc_list):
        """
        Builds a list of all testbenches and testcases
        that are selected to be run.
        """
        # Build all possible tests as starting point
        self._build_base_tests()

        # Create test output folder names
        for test in self.base_tests_container.get():
            test.create_test_output_folder_name()

        # Update status from previous failing test runs
        for old_test in re_run_tc_list:
            if old_test.get_status() == TestStatus.FAIL:
                for new_test in self.base_tests_container.get():
                    if new_test.get_test_path() == old_test.get_test_path():
                        new_test.set_status(TestStatus.FAIL)
            if old_test.get_status() == TestStatus.RE_RUN:
                for new_test in self.base_tests_container.get():
                    if new_test.get_test_path() == old_test.get_test_path():
                        new_test.set_status(TestStatus.RE_RUN)

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
            self._build_testcase()
        # Run testgroup
        elif self.project.settings.get_testgroup():
            self._build_testgroup()
        # Run only changed
        else:
            self._build_modified()

    def get_list_of_tests_to_run(self) -> list:
        """
        Returns list of all testbenches and testcases
        that are selected to be run.
        """
        return self.tests_to_run_container.get()

    def get_num_tests(self) -> int:
        return len(self.base_tests_container.get())

    # ====================================================================
    # Test builder methods
    # ====================================================================

    def _get_num_tests_to_run(self) -> int:
        return self.tests_to_run_container.num_elements()

    def _set_return_code(self, return_code):
        self.project.settings.set_return_code(return_code)

    def _str_match(self, str1, str2) -> bool:
        return str1.upper() == str2.upper()

    def _build_base_tests(self) -> None:
        """
        Build a list of all tests.
        """

        def get_api_selected_gc(tb) -> list:
            """
            Find generic container for this testbench,
            and return the list of generics.
            """
            generics_list = []
            # Locate generic container for this TB, i.e.
            # generics set by test script designer.
            for gc in self.project.generic_container.get():
                if self._str_match(gc.get_name(), tb.get_name()):
                    generics_list = gc.get()
            return generics_list

        def is_verilog_testbench(testbench) -> bool:
            return testbench.get_hdlfile().check_file_type("verilog")

        def user_has_selected_sequencer_testcase(generic_list) -> bool:
            """Checks if the user has entered a sequencer built-in testcase to run."""
            for gc in generic_list:
                for gc_item in gc:
                    if isinstance(gc_item, str):
                        if self._str_match(gc_item, sequencer_testcase_string):
                            return True
            return False

        # Remove any existing test(s)
        self.tests_to_run_container.empty_list()
        self.base_tests_container.empty_list()

        sequencer_testcase_string = self.project.settings.get_testcase_identifier_name()

        self.test_id_count = 0
        # Iterate all TBs
        for tb in self.testbench_container.get():
            api_selected_gc_list = get_api_selected_gc(tb)

            # ------------------------------------
            # Verilog TB
            # ------------------------------------
            if is_verilog_testbench(tb) is True:
                api_selected_gc_list = [
                    (generic, value) for _, (generic, value) in api_selected_gc_list
                ]

                tc_gc_selected = user_has_selected_sequencer_testcase(
                    api_selected_gc_list
                )

                # Scripted generics tests
                if api_selected_gc_list:
                    # Create tests with all sequencer built-in testcases?
                    if tc_gc_selected is False and tb.get_has_testcase():
                        for tc in tb.get_testcase():
                            for gc in api_selected_gc_list:
                                test = self._get_test_object(tb=tb)
                                test.set_gc(gc)
                                test.set_tc(tc)
                                self.tests_to_run_container.add(test)

                # No scripted generics tests
                else:
                    # Tests from detected sequencer testcases
                    for tc in tb.get_testcase():
                        test = self._get_test_object(tb=tb)
                        test.set_tc(tc)
                        self.tests_to_run_container.add(test)

            # ------------------------------------
            # VHDL TB
            # ------------------------------------
            else:
                # Generics for non-specified architecture, i.e. all architectures
                gc_list_no_arch = [
                    gc for (gc_arch, gc) in api_selected_gc_list if gc_arch is None
                ]

                # Match with architecture
                for arch in tb.get_architecture():
                    # Script generics set for this architecture
                    gc_list_this_arch = [
                        gc
                        for (gc_arch, gc) in api_selected_gc_list
                        if gc_arch is not None
                        if self._str_match(gc_arch, arch.get_name())
                    ]

                    # Combined generics list with generics set without
                    # architecture and generics set for this architecture
                    gc_list_combined = gc_list_this_arch + gc_list_no_arch

                    tc_gc_selected = user_has_selected_sequencer_testcase(
                        gc_list_combined
                    )

                    # Scripted generics tests
                    if gc_list_combined:
                        # Create tests with all sequencer built-in testcases?
                        if tc_gc_selected is False and arch.get_has_testcase():
                            for tc in arch.get_testcase():
                                for gc in gc_list_combined:
                                    test = self._get_test_object(tb=tb)
                                    test.set_arch(arch)
                                    test.set_gc(gc)
                                    test.set_tc(tc)
                                    self.tests_to_run_container.add(test)

                        # Or, user has selected sequencer built-in testcase
                        else:
                            for gc in gc_list_combined:
                                test = self._get_test_object(tb=tb)
                                test.set_arch(arch)

                                if self._str_match(gc[0], sequencer_testcase_string):
                                    test.set_tc(gc[1])
                                else:
                                    test.set_gc(gc)

                                self.tests_to_run_container.add(test)

                    # No scripted generics tests
                    else:
                        # Check if test has GC_TESTCASE setting
                        if arch.get_has_testcase() is False:
                            # Test without generics
                            test = self._get_test_object(tb=tb)
                            test.set_arch(arch)
                            self.tests_to_run_container.add(test)
                        else:
                            # Tests from detected sequencer testcases
                            for tc in arch.get_testcase():
                                test = self._get_test_object(tb=tb)
                                test.set_arch(arch)
                                test.set_tc(tc)
                                self.tests_to_run_container.add(test)

        # Copy to base list, keep in test list.
        self.base_tests_container.add_element_from_list(
            self.tests_to_run_container.get()
        )

    @staticmethod
    def _unix_match(search_string, pattern) -> bool:
        """
        Match search_string with pattern using Unix wild cards.
        Robust for non-string objects (e.g. HDLLibrary), None, etc.
        """
        import fnmatch

        # Empty/None pattern => treat as match-all (used by existing logic)
        if pattern is None or pattern == "":
            return True

        # Convert search_string to string if needed
        if search_string is None:
            search_string = ""
        elif not isinstance(search_string, str):
            # Common pattern in HDLRegression objects
            if hasattr(search_string, "get_name"):
                search_string = search_string.get_name()
            else:
                search_string = str(search_string)

        # Convert pattern to string if needed
        if not isinstance(pattern, str):
            pattern = str(pattern)

        return fnmatch.fnmatch(search_string, pattern)

    def _get_user_testcase_list(self) -> list:
        return self.project.settings.get_testcase_list()

    def _copy_filtered_tests_to_tests_to_run_container(self, filtered_tests) -> bool:
        """
        Copies the filtered tests, i.e the ones selected for run,
        from a filtered list to the tests_to_run_container.
        """
        self.tests_to_run_container.empty_list()
        for test in filtered_tests:
            self.tests_to_run_container.add(test)
        return True

    def _build_testcase(self) -> None:
        """
        Build a list of tests that match
        user selected testcase.
        """

        def _is_testcase_an_index_number():
            return all(tc[0].isdigit() for tc in testcase_list)

        def _get_testcase_index_number() -> int:
            testcase_index = int(testcase_list[0][0])
            if testcase_index >= 1:
                return testcase_index
            else:
                return None

        self.logger.debug("building tests for testcase")
        # Get user seleceted testcase
        testcase_list = self._get_user_testcase_list()

        # Select based on user input as number or testcase name
        if _is_testcase_an_index_number() is True:
            index = _get_testcase_index_number()
            if index not in range(1, self.test_id_count + 1):
                self.logger.error(
                    "Testcase index out of range (1 to %d)." % (self.test_id_count)
                )
                return None
            self._get_testcase_from_index(index)
        else:
            self._get_testcase_from_string(testcase_list)

        # Verify if any testcases were found
        if self.tests_to_run_container.num_elements() == 0:
            self._set_return_code(1)
            for testcase in testcase_list:
                self.logger.warning("No testcase match for: %s" % (testcase))

    def _get_testcase_from_index(self, index):
        """User selected testcase by number."""
        # Adjust testcase index number for array access
        index -= 1
        test = self.base_tests_container.get_index(index)
        self.tests_to_run_container.empty_list()
        self.tests_to_run_container.add(test)

    def _parse_tc_selector(self, selector: str) -> dict:
        """
        Parse a testcase selector string.

        Supported forms:
          - entity[.architecture[.testcase]]
          - library:entity[.architecture[.testcase]]
          - library:           (only library filter => match all in that lib)
          - :entity[...]       (explicit 'no library filter')

        Returns a dict:
          {"library": str|None, "entity": str|None, "architecture": str|None, "testcase": str|None}
        """
        sel = {"library": None, "entity": None, "architecture": None, "testcase": None}

        selector = (selector or "").strip()
        if not selector:
            return sel

        # Optional library prefix: "<lib>:<rest>"
        if ":" in selector:
            left, right = selector.split(":", 1)
            sel["library"] = left.strip() or None

            selector = right.strip()
            if selector == "":
                # "lib:" => only library filter
                return sel

        # Remaining: "entity[.arch[.tc]]"
        parts = [p.strip() for p in selector.split(".")]

        if len(parts) > 3:
            raise ValueError(
                "Invalid testcase selector '{}'. "
                "Expected max: [lib:]entity.architecture.testcase".format(selector)
            )

        # Keep behaviour: empty fields become None
        sel["entity"] = parts[0] or None if len(parts) >= 1 else None
        sel["architecture"] = parts[1] or None if len(parts) >= 2 else None
        sel["testcase"] = parts[2] or None if len(parts) >= 3 else None

        return sel


    def _selector_to_dict(self, sel):
        """
        Normalize selector representations into:
          {"library": None|str, "entity": None|str, "architecture": None|str, "testcase": None|str}

        Supports:
          - dict (already in format)
          - str  (e.g. "*:irqc_tb.*")
          - list/tuple legacy:
              [entity], [entity, arch], [entity, arch, tc]
            and the broken early-split form:
              ['*:irqc_tb', '*', None] -> rebuild '*:irqc_tb.*' and parse correctly
        """
        if sel is None:
            return None

        # Already dict
        if isinstance(sel, dict):
            return {
                "library": sel.get("library") or None,
                "entity": sel.get("entity") or None,
                "architecture": sel.get("architecture") or None,
                "testcase": sel.get("testcase") or None,
            }

        # Raw string selector
        if isinstance(sel, str):
            return self._parse_tc_selector(sel)

        # Legacy list/tuple selector
        if isinstance(sel, (list, tuple)):
            parts = [p for p in sel if p not in (None, "")]
            if not parts:
                return None

            # Ensure strings from this point
            parts = [str(p) for p in parts]
            first = parts[0]

            # Fix: upstream split on '.' before dealing with ':'
            if ":" in first:
                rebuilt = ".".join(parts)
                return self._parse_tc_selector(rebuilt)

            # Normal legacy: entity.arch.tc (no library in this representation)
            return {
                "library": None,
                "entity": parts[0] if len(parts) >= 1 else None,
                "architecture": parts[1] if len(parts) >= 2 else None,
                "testcase": parts[2] if len(parts) >= 3 else None,
            }

        return None


    def _get_testcase_from_string(self, testcase_list):
        selectors = []
        for raw in testcase_list:
            sel = self._selector_to_dict(raw)
            if sel is not None:
                selectors.append(sel)

        filtered_tests = []

        for test in self.base_tests_container.get():
            # NOTE: For VHDLTest, get_library() returns an HDLLibrary object
            lib_obj = test.get_library()
            lib_name = lib_obj.get_name() if lib_obj is not None else ""

            entity = test.get_name()
            architecture = test.get_arch().get_name()
            testcase = test.get_tc()

            for sel in selectors:
                # None/"" => no filter
                if sel["library"] and not self._unix_match(lib_name, sel["library"]):
                    continue
                if sel["entity"] and not self._unix_match(entity, sel["entity"]):
                    continue
                if sel["architecture"] and not self._unix_match(architecture, sel["architecture"]):
                    continue

                # If selector requests testcase, test must have tc and it must match
                if sel["testcase"]:
                    if not testcase:
                        continue
                    if not self._unix_match(testcase, sel["testcase"]):
                        continue

                filtered_tests.append(test)
                break  # OR between selectors

        self._copy_filtered_tests_to_tests_to_run_container(filtered_tests)

    def _build_testgroup(self) -> None:
        """
        Build a list of tests that are
        part of testgroup.
        """
        self.logger.debug("building tests for testgroup")
        filtered_tests = []

        # Get which testgroup to run.
        testgroup_to_run = self.project.settings.get_testgroup()

        # Get testgroup info
        testgroup = self.project._get_testgroup_container(
            testgroup_name=testgroup_to_run, create_if_not_found=False
        )

        if testgroup:
            # Locate all tests in test group
            for test_run in testgroup.get():
                # Extract test parts
                (entity, architecture, testcase, generics) = test_run

                # Check for match with test container (base tests)
                for test in self.base_tests_container.get():
                    # Match entity
                    if self._unix_match(search_string=test.get_name(), pattern=entity):
                        # Match architecture
                        if architecture:
                            if self._unix_match(
                                search_string=test.get_arch().get_name(),
                                pattern=architecture,
                            ):
                                # User selected sequencer testcase?
                                if testcase:
                                    # Match sequencer testcase
                                    if self._unix_match(
                                        search_string=test.get_tc(), pattern=testcase
                                    ):
                                        filtered_tests.append(test)
                                else:
                                    filtered_tests.append(test)
                        else:
                            filtered_tests.append(test)

        self._copy_filtered_tests_to_tests_to_run_container(filtered_tests)

        if self.tests_to_run_container.num_elements() == 0:
            self._set_return_code(1)
            self.logger.warning("No test found for test group: %s" % (testgroup_to_run))

    def _build_modified(self) -> None:
        """
        Build a list of tests that have to
        be re-run due to changes.
        """
        self.logger.debug("building tests for changed only")

        filtered_tests = []
        for test in self.base_tests_container.get():
            if test.get_hdlfile().get_need_compile() is True:
                filtered_tests.append(test)
            elif test.get_status() == TestStatus.FAIL:
                filtered_tests.append(test)
            elif test.get_status() == TestStatus.RE_RUN:
                filtered_tests.append(test)
            elif not self.project.settings.get_run_success():
                filtered_tests.append(test)
            elif test.get_hdlfile().get_library().get_need_compile() is True:
                filtered_tests.append(test)
            elif test.get_hdlfile().get_library().get_dependencies_need_compile() is True:
                filtered_tests.append(test)

        self._copy_filtered_tests_to_tests_to_run_container(filtered_tests)

    def _get_test_object(self, tb=None, arch=None, tc=None, gc=None):
        """
        Will return test object based on HDL file type.
        """
        hdlfile = tb.get_hdlfile()

        if isinstance(hdlfile, VHDLFile):
            test = VHDLTest(
                tb=tb, arch=arch, tc=tc, gc=gc, settings=self.project.settings
            )
            lib = hdlfile.get_library()
            test.set_hdlfile(hdlfile)
            test.set_library(lib)
            self.test_id_count += 1
            test.set_id_number(self.test_id_count)
            return test
        elif isinstance(hdlfile, VerilogFile):
            test = VerilogTest(tb=tb, settings=self.project.settings)
            test.set_hdlfile(hdlfile)
            self.test_id_count += 1
            test.set_id_number(self.test_id_count)
            return test
        else:
            self.logger.warning(
                "Filetype not detected for %s" % (type(tb.get_hdlfile()))
            )
            return None
