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

from .sim_runner import SimRunner
from ..report.logger import Logger
from ..scan.hdl_regex_pkg import RE_GHDL_WARNING, RE_GHDL_ERROR


class GHDLRunner(SimRunner):
    SIMULATOR_NAME = "GHDL"

    # The analyze command, -a :
    #   - analyzes/compiles one or more files, and creates an object file for each source file.

    # The elaboration command, -e, must be followed by a name of either:
    #   - a configuration unit
    #   - an entity unit
    #   - an entity unit followed by a name of an architecture unit

    # The elaborate and run command, --elab-run, elaborates and runs a unit.

    def __init__(self, project):
        super().__init__(project)
        self.logger = Logger(name=__name__, project=project)
        self.project = project

    @classmethod
    def _is_simulator(cls, simulator) -> bool:
        return simulator.upper() == cls.SIMULATOR_NAME

    def _convert_hdl_version(self, hdl_version):
        if hdl_version == "2008":
            return "08"
        elif hdl_version == "2002":
            return "02"
        elif hdl_version == "1993":
            return "93"
        elif hdl_version == "1987":
            return "87"
        else:
            return "08"

    def _get_simulator_error_regex(self):
        return RE_GHDL_ERROR

    def _get_simulator_warning_regex(self):
        return RE_GHDL_WARNING

    def _get_simulator_call(
        self,
        hdlfile=None,
        module=None,
        elab_run=False,
        generic_call=None,
        module_call=None,
    ) -> list:
        """
        Get a call for the GHDL simulator.
        Typically a HDLFILE object is used for analyze (-a),
        while a MODULE object with the elab_run parameter are used for
        elaboration (-e) and running simulations (-r).

        Returns:
            return_list(list): a list with simulator command to be used
                               with a subprocess call.
        """
        hdlfile = module.get_hdlfile() if module else hdlfile

        ghdl_executable = self._get_simulator_executable(self.SIMULATOR_NAME)
        return_list = [ghdl_executable]
        return_list.append("--elab-run" if elab_run else "-a")

        hdl_version = self._convert_hdl_version(hdlfile.get_hdl_version())

        output_path = os.path.join(
            self.project.settings.get_sim_path(), self.project.settings.get_output_path(),"library"
        )
        library_name = hdlfile.get_library().get_name()
        library_compile_path = os.path.join(output_path, library_name)
        os.makedirs(library_compile_path, exist_ok=True)

        library_compile_path = os.path.join(library_compile_path, "v" + hdl_version)
        os.makedirs(library_compile_path, exist_ok=True)

        return_list += hdlfile._get_com_options(simulator=self.SIMULATOR_NAME)
        return_list += [
            "--workdir={}".format(library_compile_path),
            "--work={}".format(library_name),
            "-P{}/".format(output_path),
        ]

        if module:
            return_list.append(module.get_name())
        else:
            return_list.append(hdlfile.get_filename_with_path())

        if elab_run:
            if module_call:
                return_list.append(module_call)
            if generic_call:
                return_list += generic_call.split(" ")

            if self.project.settings.get_gui_mode():
                wave_file_format = (
                    self.project.settings.get_simulator_wave_file_format()
                )
                self.project.settings.add_sim_options(
                    "--{}=sim.{}".format(wave_file_format, wave_file_format),
                    warning=False,
                )

            return_list += self.project.settings.get_sim_options()

        return return_list

    def _compile_library(self, library, force_compile=False) -> "HDLLibrary":
        """
        Get all libraries and compile every file in each.

        Returns:
            success(bool): True if library compilation successed.
        """
        success = True
        # Analyze files in library
        if library.get_need_compile() or force_compile:
            for hdlfile in library.get_compile_order_list():
                self.logger.debug("Recompiling file: %s" % (hdlfile.get_name()))
                cmd = self._get_simulator_call(hdlfile=hdlfile)
                # Call command runner in super-class
                if not self._run_cmd(cmd):
                    file_name = hdlfile.get_filename_with_path()
                    self.logger.error("Failed to compile %s!" % (file_name))
                    success = False
                else:
                    hdlfile.update_compile_time()

        if success:
            return library
        else:
            return None

    def _simulate(self, test, generic_call, module_call) -> None:
        """
        Elaborate and simulate module.
        """
        self.logger.debug("Running simulations.")
        # Define a transcript file and location for simulator output
        transcript_file = os.path.join(test.get_test_path(), "transcript")
        # Get simulator call for elaboration and run
        cmd = self._get_simulator_call(
            module=test.get_tb(),
            elab_run=True,
            generic_call=generic_call,
            module_call=module_call,
        )
        # Call Runner object
        success = self._run_cmd(
            command=cmd,
            path=test.get_test_path(),
            output_file=transcript_file,
            test=test,
        )
        return success

    def _get_ignored_error_detection_str(self) -> str:
        return ""
