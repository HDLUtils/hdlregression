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
from ..scan.hdl_regex_pkg import RE_RIVIERA_WARNING, RE_RIVIERA_ERROR, RE_ACTIVE_HDL_ERROR, RE_ACTIVE_HDL_WARNING


class RivieraRunner(SimRunner):

    SIMULATOR_NAME = "RIVIERA-PRO"

    def __init__(self, project):
        super().__init__(project)
        self.logger = Logger(name=__name__, project=project)
        self.project = project

    @classmethod
    def _is_simulator(cls, simulator) -> bool:
        return simulator.upper() == cls.SIMULATOR_NAME

    # =========================================================================
    #
    # Compilation
    #
    # =========================================================================

    def _get_compile_call(self, hdlfile) -> list:
        """
        Get a call for the Modelsim simulator.

        Called from: _compile_library()

        Returns:
            return_list(list): a list with simulator command to be used with a subprocess call.
        """
        libraries_path = os.path.join(
            self.project.settings.get_sim_path(),
            self.project.settings.get_output_path(),
            "library",
        )
        compile_path = os.path.join(libraries_path, hdlfile.get_library().get_name())

        hdlfile_path = os.path.join(hdlfile.get_filename_with_path())

        if self.project.settings.get_os_platform() == "windows":
            compile_path = compile_path.replace("\\", "/")
            hdlfile_path = hdlfile_path.replace("\\", "/")
        else:
            compile_path = compile_path.replace("\\", "\\\\")
            hdlfile_path = hdlfile_path.replace("\\", "\\\\")

        if hdlfile.check_file_type("vhdl") is True:
            sim_exec = self._get_simulator_executable("vcom")
        elif hdlfile.check_file_type("verilog") is True:
            sim_exec = self._get_simulator_executable("vlog")
        elif hdlfile.check_file_type("systemverilog") is True:
            sim_exec = self._get_simulator_executable("vlog")
        else:
            self.logger.error("Unknown HDLFile type")
            return []

        return_list = [sim_exec]
        return_list += hdlfile._get_com_options(simulator=self.SIMULATOR_NAME)

        # code_coverage compile arguments
        code_coverage_settings = (
            self.project.hdlcodecoverage.get_code_coverage_settings()
        )
        if hdlfile.get_code_coverage() and code_coverage_settings:
            return_list += ["+cover=%s" % (code_coverage_settings)]

        return_list += ["-work", compile_path]
        return_list += [hdlfile_path]
        return return_list

    def _compile_library(self, library, force_compile=False) -> "HDLLibrary":
        """
        Local method for creating library mapping,
        compilining all belonging files and updating
        compile status for library.

        Called from: sim_runner.compile()

        Returns:
          'HDLLibrary' (obj): an object if compile was OK, None if not.
        """
        compile_ok = True

        libraries_path = os.path.join(
            self.project.settings.get_sim_path(),
            self.project.settings.get_output_path(),
            "library",
        )
        libraries_path = os_adjust_path(libraries_path)

        # Define where library compile should be located
        library_compile_path = os.path.join(libraries_path, library.get_name())
        library_compile_path = os_adjust_path(library_compile_path)

        vmap_exec = self._get_simulator_executable("vmap")
        vlib_exec = self._get_simulator_executable("vlib")

        # Create library
        if not os.path.isdir(library_compile_path):
            self._run_cmd(command=[vlib_exec, library.get_name()], path=libraries_path)

        # Map library
        self._run_cmd(
            command=[vmap_exec, library.get_name(), library_compile_path],
            path=libraries_path,
        )

        # Loop every file object in the library and compile it.
        for hdlfile in library.get_compile_order_list():
            if hdlfile.get_is_netlist():
                continue

            if hdlfile.get_need_compile() or force_compile:
                self.logger.debug("Recompiling file: %s" % (hdlfile.get_name()))

                success = self._run_cmd(
                    command=self._get_compile_call(hdlfile), path=libraries_path
                )
                if success is False:
                    compile_ok = False
                else:
                    hdlfile.update_compile_time()

        if compile_ok:
            return library
        else:
            return None

    # =========================================================================
    #
    # Simulations
    #
    # =========================================================================
    def _get_simulator_error_regex(self):
        return RE_RIVIERA_ERROR

    def _get_simulator_warning_regex(self):
        return RE_RIVIERA_WARNING

    def _get_netlist_call(self) -> str:
        """
        Creates the netlist/back-annotated call used in
        the run.do file for simulations.

        Called from: _get_simulator_call()
        """
        # Get library container
        lib_cont = self.project._get_library_container()

        netlist_obj = [
            obj
            for lib in lib_cont.get()
            for obj in lib.get_hdlfile_list()
            if obj.get_is_netlist()
        ]
        call = ""
        for obj in netlist_obj:
            call += " %s %s=%s" % (
                self.project.settings.get_netlist_timing(),
                obj.get_netlist_instance(),
                obj.get_filename_with_path().replace("\\", "/"),
            )
        return call

    def _get_simulator_do_cmd(self, test, generic_call, module_call) -> str:
        """
        Returns a Riviera-PRO simulate command (vsim) with parameters for use in run.do.
        This command does NOT include the path to vsim, since vsim is a command
        recognized by Riviera-PRO while executing do files.

        Called from: _write_run_do_file()
        """

        code_coverage_file = self.project.hdlcodecoverage.get_code_coverage_file()

        if code_coverage_file:
            # Extract the filename from path (test/coverage/<coverage_file>)
            code_coverage_file = os.path.basename(code_coverage_file)
            code_coverage_file = "./" + code_coverage_file
            code_coverage_file = code_coverage_file.replace("\\", "/")
            # Construct code_coverage save call
            code_coverage_call_save = "coverage save -onexit %s;" % (code_coverage_file)
            code_coverage_call_enable = "-coverage"
        else:
            code_coverage_call_save = ""
            code_coverage_call_enable = ""

        sim_options = " ".join(self.project.settings.get_sim_options())

        netlist_call = self._get_netlist_call()

        return " ".join(
            [   "amap",
                "-link",
                "../../../library\n",
                "vsim",
                generic_call,
                module_call,
                sim_options,
                netlist_call,
                code_coverage_call_enable,
                "; onerror {quit -code 1};",
                "onbreak {resume};",
                "run",
                "-all;",
                code_coverage_call_save,
                "exit",
            ]
        )

    def _write_run_do_file(self, test, generic_call, module_call):
        """
        Creates the run.do file that is called for starting the simulations.
        """
        sim_call = self._get_simulator_do_cmd(test, generic_call, module_call)
        run_file = os.path.join(test.get_test_path(), "run.do")
        try:
            with open(run_file, "w") as file:
                file.writelines(sim_call.strip())
        except Exception:
            raise OutputFileError(run_file)

    def _simulate(self, test, generic_call, module_call) -> bool:
        """
        Runs the run.do file that starts the simulations.
        """
        sim_exec = self._get_simulator_executable("vsim")
        command = [sim_exec, "-c", "-do", "do run.do"]

        success = self._run_cmd(command=command, path=test.get_test_path(), test=test)
        return success

    def _get_module_call(self, test, architecture_name):
        lib_name = test.get_library().get_name()
        return "-lib {} {} {}".format(lib_name, test.get_name(), architecture_name)

    def _get_descriptive_test_name(self, test, architecture_name, module_call):
        test_name = module_call.replace("-lib ", "").replace(" ", ".")
        return test_name

    def _get_ignored_error_detection_str(self) -> str:
        return r"^\/\/  (Reconnected|Lost connection) to license server"



class ActiveHDLRunner(RivieraRunner, SimRunner):
    """
    This class is used to run Active-HDL simulations.
    It inherits from RivieraRunner since Active-HDL is a part of the Riviera-PRO suite.
    """

    SIMULATOR_NAME = "ACTIVE-HDL"

    @classmethod
    def _is_simulator(cls, simulator) -> bool:
        return simulator.upper() == cls.SIMULATOR_NAME
    
    def _get_simulator_error_regex(self):
        return RE_ACTIVE_HDL_ERROR

    def _get_simulator_warning_regex(self):
        return RE_ACTIVE_HDL_WARNING

    def _get_descriptive_test_name(self, test, architecture_name, module_call):
        test_name = module_call.replace("-lib ", "").replace(" ", ".")
        return test_name


#    def _get_module_call(self, test, architecture_name):
#        lib_name = test.get_library().get_name()
#        return "-lib {} {} {}".format(lib_name, test.get_name(), architecture_name)