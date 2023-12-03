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

from xml.etree import ElementTree as ET
from xml.dom import minidom
from .hdlreporter import HDLReporter

class XMLReporter(HDLReporter):
    '''
    HDLReporter sub-class for documenting testcase run
    to an XML file.
    '''

    def __init__(self, project=None, filename=None):
        super().__init__(project=project, filename=filename)

    def write_to_file(self) -> None:
        '''
        Writes regression run result to file in XML format.
        '''

        report = ET.Element("TestReport")

        # Write settings
        settings = ET.SubElement(report, "Settings")
        ET.SubElement(settings, "CI_run").text = str(self._is_ci_run())
        ET.SubElement(settings, "Testcase_run").text = str(self._is_testcase_run())
        ET.SubElement(settings, "Testgroup_run").text = str(self._is_testgroup_run())
        ET.SubElement(settings, "GUI_mode").text = str(self._is_gui_run())
        ET.SubElement(settings, "Time_of_run").text = str(self._time_of_run())
        ET.SubElement(settings, "Time_of_sim").text = str(self._time_of_sim())

        # Write test results
        results = ET.SubElement(report, "Results")

        passing_tests, fail_tests, not_run_tests = self.project.get_results()

        pass_elem = ET.SubElement(results, "Passing")
        for test in passing_tests:
            ET.SubElement(pass_elem, "Test").text = test

        fail_elem = ET.SubElement(results, "Failing")
        for test in fail_tests:
            ET.SubElement(fail_elem, "Test").text = test

        not_run_elem = ET.SubElement(results, "NotRun")
        for test in not_run_tests:
            ET.SubElement(not_run_elem, "Test").text = test

        # Write testcase info
        testcases = ET.SubElement(report, "Testcases")
        for library in self.project.library_container.get():
            for hdlfile in library.get_hdlfile_list():
                for tb_module in hdlfile.get_tb_modules():
                    for arch_module in tb_module.get_architecture():
                        testcase_elem = ET.SubElement(testcases, "Testcase")
                        ET.SubElement(testcase_elem, "ModuleName").text = tb_module.get_name()
                        ET.SubElement(testcase_elem, "ArchitectureName").text = arch_module.get_name()

        # Write testgroup info
        testgroups = ET.SubElement(report, "Testgroups")
        for testgroup_container in self.project.testgroup_collection_container.get():
            testgroup_elem = ET.SubElement(testgroups, "Testgroup")
            ET.SubElement(testgroup_elem, "Name").text = testgroup_container.get_name()
            for idx, testgroup_items_list in enumerate(testgroup_container.get()):
                entity, architecture, testcase, generics = tuple(testgroup_items_list)
                tg_str = '%s' % entity
                if architecture:
                    tg_str += '.%s' % architecture
                if testcase:
                    tg_str += '.%s' % testcase
                if generics:
                    tg_str += ', generics=%s' % generics
                ET.SubElement(testgroup_elem, "Item").text = tg_str

        # Write compilation order
        if self.get_report_compile_order():
            comp_order = ET.SubElement(report, "CompilationOrder")
            for library in self.project.library_container.get():
                library_elem = ET.SubElement(comp_order, "Library")
                ET.SubElement(library_elem, "LibraryName").text = library.get_name()
                for idx, module_instance in enumerate(library.get_compile_order_list()):
                    module_elem = ET.SubElement(library_elem, "Module")
                    tb = "(TB)" if module_instance.get_is_tb() else ""
                    ET.SubElement(module_elem, "ModuleName").text = module_instance.get_filename() + " " + tb

        # Write library info
        if self.get_report_library():
            library_info = ET.SubElement(report, "LibraryInformation")
            for library in self.project.library_container.get():
                library_elem = ET.SubElement(library_info, "Library")
                ET.SubElement(library_elem, "LibraryName").text = library.get_name()
                for module in library._get_list_of_lib_modules():
                    module_elem = ET.SubElement(library_elem, "Module")
                    ET.SubElement(module_elem, "ModuleType").text = module.get_type()
                    ET.SubElement(module_elem, "ModuleName").text = module.get_name()

        # Do not create report if no test was run
        if self._check_test_was_run():
            # Convert the XML tree to a prettified string
            xml_string = ET.tostring(report, encoding="unicode", method="xml")
            formatted_xml = minidom.parseString(xml_string).toprettyxml(indent="    ")

            # Write the formatted XML string to file
            with open(self.get_full_filename(), 'w') as lf:
                lf.write(formatted_xml)
