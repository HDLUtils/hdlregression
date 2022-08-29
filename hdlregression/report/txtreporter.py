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


if __package__ is None or __package__ == '':
    from hdlreporter import HDLReporter
else:
    from .hdlreporter import HDLReporter


class TXTReporter(HDLReporter):
    '''
    HDLReporter sub-class for documenting testcase runs
    to a .TXT file.
    '''

    def __init__(self, project=None, filename=None):
        super().__init__(project=project, filename=filename)

    def write_to_file(self) -> None:
        '''
        Wites regression run result to file.
        '''

        # Do not create report if no test was run
        if self._check_test_was_run():
            with open(self.get_full_filename(), 'a') as lf:

                # Write settings for this run
                lf.write('\nTest run settings:\n')
                lf.write('CI run        : %s\n' % (self._is_ci_run()))
                lf.write('Testcase run  : %s\n' % (self._is_testcase_run()))
                lf.write('Testgroup run : %s\n' % (self._is_testgroup_run()))
                lf.write('GUI mode      : %s\n' % (self._is_gui_run()))
                lf.write('Time of run   : %s\n' % (self._time_of_run()))
                lf.write('Time of sim   : %s ms.\n' % (self._time_of_sim()))

                # Write test results
                pass_tests, fail_tests = self.project.get_results()
                lf.write('\n\nPassing tests (%d):\n' % (len(pass_tests)))
                for test in pass_tests:
                    lf.write(test + '\n')
                lf.write('\nFailing tests (%d):\n' % (len(fail_tests)))
                for test in fail_tests:
                    lf.write(test + '\n')

                # Write testcases
                lf.write('\n\n')
                for library in self.project.library_container.get():
                    # All files
                    for hdlfile in library.get_hdlfile_list():
                        # All TB modules in file
                        for tb_module in hdlfile.get_tb_modules():
                            # All architectures connected with this TB
                            for arch_module in tb_module.get_architecture():
                                lf.write('Testcase: %s.%s\n' % (tb_module.get_name(), arch_module.get_name()))
                                # All testcases connected with this architecture
                                for testcase in arch_module.get_testcase():
                                    lf.write('Testcase: %s.%s.%s\n' % (tb_module.get_name(), arch_module.get_name(), testcase))

                # Write testgroups
                lf.write('\n\n')
                for testgroup_container in self.project.testgroup_collection_container.get():
                    lf.write('Testgroup: ' + testgroup_container.get_name() + '\n')
                    testgroup_items_list = testgroup_container.get()
                    for idx, testgroup_items_list in enumerate(testgroup_container.get()):
                        entity, architecture, testcase, generics = tuple(testgroup_items_list)
                        tg_str = '%d: %s' % (idx+1, entity)
                        if architecture:
                            tg_str += '.%s' % (architecture)
                        if testcase:
                            tg_str += '.%s' % (testcase)
                        if generics:
                            tg_str += ', generics=%s' % (generics)
                        lf.write(tg_str + '\n')

                # Write compilation order
                if self.get_report_compile_order():
                    lf.write('\n\nCompilation order:\n')
                    for library in self.project.library_container.get():
                        lf.write('Library ' + library.get_name() + ':\n')
                        for idx, module_instance in enumerate(library.get_compile_order_list()):
                            tb = "(TB)" if module_instance.get_is_tb() else ""
                            lf.write('  File %d: %s %s\n' % (idx+1, module_instance.get_filename(), tb))

                # Write library information
                if self.get_report_library():
                    lf.write('\nLibrary information:\n')
                    for library in self.project.library_container.get():
                        lf.write('  %s:\n' % (library.get_name()))
                        for module in library.get_list_of_library_modules():
                            lf.write('    %s: %s\n' % (module.get_type(), module.get_name()))
