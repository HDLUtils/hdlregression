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


class JSONReporter(HDLReporter):

    def __init__(self, project=None, filename=None):
        super().__init__(project=project, filename=filename)

    def write_to_file(self) -> None:
        '''
        Writes testcase run results to file.
        '''

        # Only create report if test was run
        if self._check_test_was_run():

            # Write settings for this run
            data = '''
{
    "Test run settings" :
        {
            "CI run" : "%s",
            "Testcase run" : "%s",
            "Testgroup run" : "%s",
            "GUI mode" : "%s",
            "Time of run" : "%s",
            "Time of sim" : "%s"
        }''' % (self._is_ci_run(),
                self._is_testcase_run(),
                self._is_testgroup_run(),
                self._is_gui_run(),
                self._time_of_run(),
                self._time_of_sim())

            # Write test results
            pass_tests, fail_tests = self.project.get_results()
            pass_test_str = ''
            fail_test_str = ''
            for idx, test in enumerate(pass_tests):
                if idx + 1 == len(pass_tests):
                    if len(fail_tests) == 0:
                        pass_test_str += '"%s" : "PASS"\n' % (test)
                    else:
                        pass_test_str += '"%s" : "PASS",\n' % (test)
                else:
                    pass_test_str += '"%s" : "PASS",\n' % (test)
            for idx, test in enumerate(fail_tests):
                if idx + 1 == len(fail_tests):
                    fail_test_str += '"%s" : "FAIL"\n' % (test)
                else:
                    fail_test_str += '"%s" : "FAIL",\n' % (test)

            data += '''
    "Test results" :
        {
            %s''' % (pass_test_str)
            if fail_test_str:
                data += '''
            %s''' % (fail_test_str)
            data += '''
        }
'''

            # Write testcases
            data += '''
    "Testcase" : ['''
            for library in self.project.library_container.get():
                # All files
                for hdlfile in library.get_hdlfile_list():
                    # All TB modules in file
                    for tb_module in hdlfile.get_tb_modules():
                        # All architectures connected with this TB
                        for idx, arch_module in enumerate(tb_module.get_architecture()):
                            # TODO! Fix commas
                            data += '''
            {
                "Name" : "%s.%s"
            },''' % (tb_module.get_name(), arch_module.get_name())
                            # All testcases connected with this architecture
                            for testcase in arch_module.get_testcase():
                                # TODO! Fix commas
                                data += '''
            {
                "Name" : "%s.%s.%s"
            },''' % (tb_module.get_name(), arch_module.get_name(), testcase)
            data += '''
                ],
            '''

            # Write testgroups
            data += '''
    "Testgroup" : ['''
            for testgroup_container in self.project.testgroup_collection_container.get():
                data += '''
            {
            "Name" : "%s"
            "Items" : [''' % (testgroup_container.get_name())
                testgroup_items_list = testgroup_container.get()
                for idx, testgroup_items_list in enumerate(testgroup_container.get()):
                    entity, architecture, testcase, generics = tuple(testgroup_items_list)
                    tg_str = '%s' % (entity)
                    if architecture:
                        tg_str += '.%s' % (architecture)
                    if testcase:
                        tg_str += '.%s' % (testcase)
                    if generics:
                        tg_str += ', generics=%s' % (generics)
                    data += '''
                "Name" : "%s",''' % (tg_str)
                data += '''
                    ],'''
                data += '''
                },'''
            data += '''
            ]'''

            # Write compilation order
            if self.get_report_compile_order():
                data += ''',
    "Compile_order" : ['''
                for library in self.project.library_container.get():
                    data += '''
                "Library" : "%s"
                "Module" : [''' % (library.get_name())
                    for idx, module_instance in enumerate(library.get_compile_order_list()):
                        tb = "(TB)" if module_instance.get_is_tb() else ""
                        data += '''
                        {
                            "name" : "%s",
                            "tb" : "%s"
                        }''' % (module_instance.get_filename(), tb)
                    data += '''
                            ],'''
                data += '''
                        ]'''

                # Write library information
                if self.get_report_library():
                    data += ''',
    "Library_info" : ['''
                    for library in self.project.library_container.get():
                        data += '''
                    {
                        "Name" : "%s",
                        "Items" : [''' % (library.get_name())
                        for module in library.get_list_of_library_modules():
                            data += '''
                                {
                                    "type" : "%s",
                                    "name" : "%s"
                                },''' % (module.get_type(), module.get_name())
                        data += '''
                            ]
                    },'''
                    data += '''
                    ]'''

            data += '''
}'''
            with open(self.get_full_filename(), 'a') as lf:
                lf.write(data)
