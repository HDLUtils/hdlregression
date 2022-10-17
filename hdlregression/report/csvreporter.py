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

import csv

from .hdlreporter import HDLReporter


class CSVReporter(HDLReporter):
    '''
    HDLReporter sub-class for documenting testcase runs
    to a .CSV file.
    '''

    def __init__(self, project=None, filename=None):
        super().__init__(project=project, filename=filename)

    def write_to_file(self) -> None:
        '''
        Writes testcase run results to file.
        '''

        # Only create report if test was run
        if self._check_test_was_run():

            # Open the log file
            with open(self.get_full_filename(), mode='w') as log_file:
                lf = csv.writer(log_file, delimiter=',')

                # Write settings for this run
                lf.writerow(['Test run settings:'])
                lf.writerow(['CI run', '%s' % (self._is_ci_run())])
                lf.writerow(['Testcase run', '%s' % (self._is_testcase_run())])
                lf.writerow(['Testgroup run', '%s' % (self._is_testgroup_run())])
                lf.writerow(['GUI mode', '%s' % (self._is_gui_run())])
                lf.writerow(['Time of run', '%s' % (self._time_of_run())])
                lf.writerow(['Time of sim', '%s ms.' % (self._time_of_sim())])

                lf.writerow([])
                lf.writerow([])
                # Write test results
                pass_tests, fail_tests = self.project.get_results()
                lf.writerow(['Passing tests (%d):' % (len(pass_tests))])
                for test in pass_tests:
                    lf.writerow([test])

                lf.writerow([])
                lf.writerow([])
                lf.writerow(['Failing tests (%d):' % (len(fail_tests))])
                for test in fail_tests:
                    lf.writerow([test])

                # Write testcases
                lf.writerow([])
                for library in self.project.library_container.get():
                    # All files
                    for hdlfile in library.get_hdlfile_list():
                        # All TB modules in file
                        for tb_module in hdlfile.get_tb_modules():
                            # All architectures connected with this TB
                            for arch_module in tb_module.get_architecture():
                                lf.writerow(['Testcase:', '%s.%s' % (tb_module.get_name(), arch_module.get_name())])
                                # All testcases connected with this architecture
                                for testcase in arch_module.get_testcase():
                                    lf.writerow(['Testcase:', '%s.%s.%s' % (tb_module.get_name(), arch_module.get_name(), testcase)])

                # Write testgroups
                lf.writerow([])
                for testgroup_container in self.project.testgroup_collection_container.get():
                    lf.writerow([])
                    lf.writerow(['Testgroup: ' + testgroup_container.get_name()])
                    testgroup_items_list = testgroup_container.get()
                    for idx, testgroup_items_list in enumerate(testgroup_container.get()):
                        entity, architecture, testcase, generics = tuple(testgroup_items_list)
                        tg_str = '%d %s' % (idx + 1, entity)
                        if architecture:
                            tg_str += '.%s' % (architecture)
                        if testcase:
                            tg_str += '.%s' % (testcase)
                        if generics:
                            tg_str += ', generics=%s' % (generics)
                        lf.writerow([tg_str])

                # Write compilation order
                if self.get_report_compile_order():
                    lf.writerow([])
                    lf.writerow([])
                    lf.writerow(['Compilation order:'])
                    for library in self.project.library_container.get():
                        lf.writerow([])
                        lf.writerow(['Library', library.get_name()])
                        for idx, module_instance in enumerate(library.get_compile_order_list()):
                            tb = "(TB)" if module_instance.get_is_tb() else ""
                            lf.writerow(['File %d' % (idx + 1), module_instance.get_filename(), tb])

                # Write library information
                if self.get_report_library():
                    lf.writerow([])
                    lf.writerow([])
                    lf.writerow(['Library information'])
                    for library in self.project.library_container.get():
                        lf.writerow([])
                        lf.writerow(['Library %s:' % (library.get_name())])
                        for module in library.get_list_of_library_modules():
                            lf.writerow([module.get_type(), module.get_name()])
