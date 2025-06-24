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

from .sim_runner import SimRunner, OutputFileError
from ..report.logger import Logger
from ..hdlregression_pkg import os_adjust_path
from ..scan.hdl_regex_pkg import RE_VIVADO_WARNING, RE_VIVADO_ERROR

class VivadoRunner(SimRunner):

    SIMULATOR_NAME = "XSIM"

    def __init__(self, project):
        super().__init__(project)
        self.logger = Logger(name=__name__, project=project)
        self.project = project

    @classmethod
    def _is_simulator(cls, simulator) -> bool:
        return (simulator.upper() == cls.SIMULATOR_NAME)

    def _get_compile_call(self, hdlfile) -> list:
        libraries_path = os.path.join(self.project.settings.get_sim_path(), self.project.settings.get_output_path(), 'library')
        compile_path = os.path.join(libraries_path, hdlfile.get_library().get_name())
        hdlfile_path = os.path.join(hdlfile.get_filename_with_path())

        # Adjust path separators for OS
        if self.project.settings.get_os_platform() == "windows":
            compile_path = compile_path.replace('\\', '/')
            hdlfile_path = hdlfile_path.replace('\\', '/')
        else:
            compile_path = compile_path.replace('\\', '\\\\')
            hdlfile_path = hdlfile_path.replace('\\', '\\\\')

        if hdlfile.check_file_type('vhdl'):
            sim_exec = 'xvhdl'
        elif hdlfile.check_file_type('verilog') or hdlfile.check_file_type('systemverilog'):
            sim_exec = 'xvlog'
        else:
            self.logger.error('Unknown HDLFile type')
            return []

        #return_list = [sim_exec, "-work", hdlfile.get_library().get_name(), compile_path, hdlfile_path]
        return_list = [sim_exec, "-work", hdlfile.get_library().get_name(), hdlfile_path]
        return_list += hdlfile._get_com_options(simulator=self.SIMULATOR_NAME)

        # Add code coverage arguments if needed
        if hdlfile.get_code_coverage() and self.project.hdlcodecoverage.get_code_coverage_settings():
            return_list += ['--coverage']

        return return_list

    def _compile_library(self, library, force_compile=False) -> 'HDLLibrary':
        compile_ok = True
        libraries_path = os.path.join(self.project.settings.get_sim_path(), self.project.settings.get_output_path(), 'library')
        libraries_path = os_adjust_path(libraries_path)

        # Library compile path
        library_compile_path = os.path.join(libraries_path, library.get_name())
        library_compile_path = os_adjust_path(library_compile_path)

        # Compile each HDL file
        for hdlfile in library.get_compile_order_list():
            if hdlfile.get_is_netlist():
                continue

            if hdlfile.get_need_compile() or force_compile:
                self.logger.debug('Recompiling file: %s' % (hdlfile.get_name()))
                success = self._run_cmd(command=self._get_compile_call(hdlfile), path=libraries_path)
                if not success:
                    compile_ok = False
                else:
                    hdlfile.update_compile_time()

        return library if compile_ok else None

    def _get_simulator_error_regex(self):
        return RE_VIVADO_ERROR

    def _get_simulator_warning_regex(self):
        return RE_VIVADO_WARNING

    def _get_netlist_call(self) -> str:
        return ''

    def _get_simulator_do_cmd(self, test, generic_call, module_call) -> str:
        sim_options = ' '.join(self.project.settings.get_sim_options())
        return ' '.join(['xsim', generic_call, module_call, sim_options, '-R'])

    def _write_run_do_file(self, test, generic_call, module_call):
        sim_call = self._get_simulator_do_cmd(test, generic_call, module_call)
        run_file = os.path.join(test.get_test_path(), 'run.do')
        try:
            with open(run_file, 'w') as file:
                file.write(sim_call.strip())
        except Exception as e:
            raise OutputFileError(run_file)

    def _simulate(self, test, generic_call, module_call) -> bool:
        print('--->> starting sim')
        command = ['xsim', '--runall', 'run.do']
        success = self._run_cmd(command=command, path=test.get_test_path(), test=test)
        print('---->>> sim done')
        return success

    def _get_ignored_error_detection_str(self) -> str:
        # This should include any XSIM-specific ignored errors
        return r'^\/\/  (Reconnected|Lost connection) to license server'
