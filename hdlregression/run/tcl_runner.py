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

import os, re

from .cmd_runner import CommandRunner
from .runner_modelsim import ModelsimRunner
from .runner_aldec import RivieraRunner, ActiveHDLRunner
from .testbuilder import TestBuilder
from ..report.logger import Logger
from ..hdlregression_pkg import os_adjust_path


class TclRunnerBase():
    """
    Base class for TclRunner functionality.
    Contains shared logic for all TclRunner implementations.
    """

    def __init__(self, project=None):
        super().__init__(project)
        self.logger = Logger(name=__name__, project=project)
        self.logger.debug("TclRunner active.")
        self.project = project
        self.test_folder = None
        self.gui_do_file = None
        self.python_exec = self.project.settings.get_python_exec()

        self.runner = None
        # Build test list
        self.testbuilder = TestBuilder(project=project)
        self.test_call = None
        self.test_name = None

    def _set_test_specifics(self, test):
        pass

    def simulate_gui(self) -> None:
        raise NotImplementedError(
            "TclRunnerBase.simulate_gui must be overridden in subclasses.")

    def _is_simulator(self, simulator) -> bool:
        raise NotImplementedError(
            "TclRunnerBase._is_simulator must be overridden in subclasses.")

    def _create_gui_do_file(self, test) -> None:
        """
        Creates a gui.do file for the tcl file.
        """
        gui_do_file = self._get_test_path(filename="gui.do", test=test)

        # with open(self.tcl_file, 'w') as cf:
        with open(gui_do_file, "w") as cf:
            cf.write(self._get_proc(test))
            cf.write(self._init(test))

    def _set_os_environment(self):
        ini_path = self._get_modelsim_ini_path()
        if ini_path:
            os.environ[self.get_simulator_name()] = ini_path

    def _load_simulator(self, test) -> int:
        """
        This method should be overridden in subclasses to implement
        simulator-specific loading logic.
        """
        raise NotImplementedError(
            "TclRunnerBase._load_simulator must be overridden in subclasses.")

    def _get_test_path(self, filename="", test=None) -> str:
        sim_path = self.project.settings.get_sim_path()
        test_path = test.get_test_path()
        return_path = os.path.join(sim_path, test_path, filename)
        return os_adjust_path(return_path)
    
    def get_sim_path(self) -> str:
        pass

    def _cd_sim(self) -> str:
        sim_path = self.get_sim_path().replace("\\", "//")
        txt = """
proc _cd_sim {} {
    eval {cd %s}
}
""" % (
            sim_path
        )
        return txt

    def _get_menu(self) -> str:
        txt = """
proc h {} {
    quietly set test_name {%s}
    puts   ""
    puts   "-----------------------------"
    puts   "- HDLRegression test runner -"
    puts   "-----------------------------"
    puts   ""
    puts   "Script commands are:"
    puts   ""
    puts   " s = Start simulation"
    puts   " r = Recompile changed and dependent files"
    puts   "ra = Recompile All and restart"
    puts   "ro = Recompile Only"
    puts   "rs = ReStart"
    puts   "rr = Restart and Run"
    puts   " h = Help (this menu)"
    puts   " q = Quit (this test run)"
    puts   "qc = Quit Completely (regression)"
    puts   ""
    puts   "Current test:"
    puts   "$test_name"
    puts   ""
}
""" % (
            self.test_name
        )
        return txt


    def _simulate(self, test) -> str:
        pass

    def _recompile_changed(self) -> str:
        cmd = "{{*}}{} -c \"import sys; sys.path.append('{}'); ".format(
            self.python_exec,
            self.project._get_install_path()
        )
        cmd += 'from hdlregression import HDLRegression; hu = HDLRegression(init_from_gui=True); hu._start_gui()" --compileChanges'
        txt = """
proc r {} {
    set cmd_show {%s}

    puts "Re-compiling changes using command ${cmd_show}"

    set chan [open |[list %s] r]

    set hdlregression_success false
    while {[gets $chan line] >= 0} {
        if {[return_checker $line] == true} {
            set hdlregression_success true
        }
    }

    if {$hdlregression_success == true} {
        puts "-----------------------------------"
        puts "     Re-compilation success!"
        puts "-----------------------------------"
    } else {
        puts "-----------------------------------"
        puts "     Re-compilation FAILED!"
        puts "-----------------------------------"
    }
}
""" % (
            cmd,
            cmd,
        )
        return txt

    def _recompile_all(self) -> str:
        cmd = "{{*}}{} -c \"import sys; sys.path.append('{}'); ".format(
            self.python_exec,
            self.project._get_install_path()
        )
        cmd += 'from hdlregression import HDLRegression; hu = HDLRegression(init_from_gui=True); hu._start_gui()" --compileAll'
        txt = """
proc ra {} {
    set cmd_show {%s}

    puts "Re-compiling all using command ${cmd_show}"

    set chan [open |[list %s] r]

    set hdlregression_success false
    while {[gets $chan line] >= 0} {
        if {[return_checker $line] == true} {
            set hdlregression_success true
        }
    }

    if {$hdlregression_success == true} {
        puts "-----------------------------------"
        puts "     Re-compilation success!"
        puts "-----------------------------------"
        rs
    } else {
        puts "-----------------------------------"
        puts "     Re-compilation FAILED!"
        puts "-----------------------------------"
    }
}
""" % (
            cmd,
            cmd,
        )
        return txt

    def _recompile_all_only(self) -> str:
        cmd = "{{*}}{} -c \"import sys; sys.path.append('{}'); ".format(
            self.python_exec,
            self.project._get_install_path()
        )
        cmd += 'from hdlregression import HDLRegression; hu = HDLRegression(init_from_gui=True); hu._start_gui()" --compileAll'
        txt = """
proc ro {} {
    set cmd_show {%s}

    puts "Re-compiling all using command ${cmd_show}"

    set chan [open |[list %s] r]

    set hdlregression_success false
    while {[gets $chan line] >= 0} {
        if {[return_checker $line] == true} {
            set hdlregression_success true
        }
    }

    if {$hdlregression_success == true} {
        puts "-----------------------------------"
        puts "     Re-compilation success!"
        puts "-----------------------------------"
    } else {
        puts "-----------------------------------"
        puts "     Re-compilation FAILED!"
        puts "-----------------------------------"
    }
}
""" % (
            cmd,
            cmd,
        )
        return txt

    @staticmethod
    def _restart_and_run() -> str:
        pass

    @staticmethod
    def _restart() -> str:
        pass

    @staticmethod
    def _quit_complete() -> str:
        txt = """
proc qc {} {
    quit -code $::quit_force
}
"""
        return txt

    @staticmethod
    def _quit() -> str:
        txt = """
proc q {} {
    quit
}
"""
        return txt

    def _get_proc(self, test) -> str:
        txt = self._get_menu()
        txt += self._cd_sim()
        txt += self._simulate(test=test)
        txt += self._recompile_all()
        txt += self._recompile_all_only()
        txt += self._recompile_changed()
        txt += self._get_checker_proc()
        txt += self._restart()
        txt += self._restart_and_run()
        txt += self._quit()
        txt += self._quit_complete()
        txt += self._get_quietly()
        return txt

    def _init(self, test=None) -> str:
        modelsim_ini = self._get_modelsim_ini_path()
        test_call = "vsim "
        test_call += self.test_call
        if modelsim_ini:
            test_call += " -modelsimini {" + modelsim_ini + "};"
        pre_sim_tcl_command = self.project.settings.simulator_settings.get_pre_sim_tcl_command()
        txt = """
# Define exit codes
quietly set quit_normal 0
quietly set quit_error 1
quietly set quit_force 2
# Load
eval {%s}
# Run pre sim command 
%s
# Display information header and menu options
h
""" % (
            test_call,
            pre_sim_tcl_command,
        )
        return txt

    @staticmethod
    def _get_quietly() -> str:
        txt = """
# Overload quietly (Modelsim specific command) to let it work in Riviera-Pro
proc quietly { args } {
  if {[llength $args] == 0} {
    puts "quietly"
  } else {
    # this works since tcl prompt only prints the last command given. list prints "".
    uplevel $args; list;
  }
}
"""
        return txt

    @staticmethod
    def _get_checker_proc() -> str:
        txt = """
proc return_checker {return_line} {
    puts "HDLRegression: ${return_line}"

    if [regexp -nocase {[\\s+]?hdlregression:success} $return_line matchresult] then {
        return true
    } else {
        return false
    }
}
"""
        return txt



class TclRunnerModelsim(TclRunnerBase, ModelsimRunner):
    """
    A TclRunner specifically for Modelsim.
    """

    def __init__(self, project=None):
        super().__init__(project)

    def _set_test_specifics(self, test):
        """
        Sets the current test name (entity.architecture.testcase) and
        the current vsim testcase call, i.e. entity(architecture) -gGC_TESTCASE=<testcase>
        """
        self.test_name = test.get_testcase_name()

        self.test_call = test.get_library().get_name() + "." + test.get_name()
        # VHDL architecture
        self.test_call += (
            "(" + test.get_arch().get_name() + ") "
            if test.get_is_vhdl() is True
            else " "
        )
        # Sequencer built-in testcase
        self.test_call += test.get_gc_str() + " "

        self.test_call += " ".join(self.project.settings.get_sim_options())

        self.test_call += self._get_netlist_call()

    def _load_simulator(self, test) -> int:
        """
        This method should be overridden in subclasses to implement
        simulator-specific loading logic.
        """
        self._set_os_environment()
        gui_do_file = self._get_test_path(filename="gui.do", test=test)
        sim_exe = self._get_simulator_executable("vsim")
        command = [sim_exe]
        command += ["-gui"]
        command += ["-do"]
        command += [gui_do_file]
        self.runner = CommandRunner(project=self.project)
        rc = self.runner.gui_run(command=command)
        return int(rc[2])
    
    def get_sim_path(self) -> str:
        return os_adjust_path(self.project.settings.get_sim_path())

    @staticmethod
    def _restart_and_run() -> str:
        txt = """
proc rr {} {
    restart -f; run -all
}
"""
        return txt

    @staticmethod
    def _restart() -> str:
        txt = """
proc rs {} {
    restart -f
}
"""
        return txt

    def _is_simulator(self, simulator) -> bool:
        return simulator.upper() == self.get_simulator_name()

    def _simulate(self, test) -> str:
        transcript_file = self._get_test_path(filename="transcript", test=test)
        txt = """
proc s {} {
    puts "Running test: %s"
    restart -f; run -all; transcript file %s
}
""" % (
            self.test_name,
            transcript_file,
        )
        return txt

    def simulate_gui(self) -> None:
        # Get tests to run
        tests = self.testbuilder.get_list_of_tests_to_run()

        # Run tests
        for test in tests:
            # Create unique test output folder
            self._create_test_folder(test.get_test_path())

            self._set_test_specifics(test)
            self._create_gui_do_file(test)

            # Start simulator
            rc = self._load_simulator(test)
            if rc == 2:
                self.logger.info("Test run aborted by user.")
                return None
            elif rc == 1:
                self.logger.warning("Failure running test, aborting.")

class TclRunnerRiviera(TclRunnerBase, RivieraRunner):
    """
    A TclRunner specifically for Riviera-Pro.
    """

    def __init__(self, project=None):
        super().__init__(project)

    def _get_library_setup(self, _test) -> str:
        cfg = os.path.join(
            self.project.settings.get_sim_path(),
            "hdlregression", "library", "library.cfg"
        )
        lines = []
        with open(cfg) as fh:
            for ln in fh:
                if ln.startswith("$") or not ln.strip():
                    continue
                name, libfile = re.match(r"(\w+)\s*=\s*\"(.+?\.lib)\"", ln).groups()
                phys = os.path.join(
                    self.project.settings.get_sim_path(),
                    "hdlregression", "library",
                    os.path.dirname(libfile)
                ).replace("\\", "/")
                lines.append(f"catch {{ vmap -del {name} }}")
                lines.append(f"vmap {name} \"{phys}\"")
        return "\n".join(lines) + "\n"

    def _init(self, test) -> str:
        modelsim_ini = self._get_modelsim_ini_path()
        lib_setup = self._get_library_setup(test)
        lib_setup = self._get_library_setup(test)
    
        test_call = f"{lib_setup}vsim {self.test_call}"
        if modelsim_ini:
            test_call += " -modelsimini {" + modelsim_ini + "};"
        pre_sim_tcl_command = self.project.settings.simulator_settings.get_pre_sim_tcl_command()
        txt = """
    # Define exit codes
    quietly set quit_normal 0
    quietly set quit_error 1
    quietly set quit_force 2
    # Create library and map it
    %s
    # Load
    eval {%s}
    # Run pre sim command 
    %s
    # Display information header and menu options
    h
    """ % (
            lib_setup,
            test_call,
            pre_sim_tcl_command,
        )
        return txt

    def _set_test_specifics(self, test):
        """
        Sets the current test name (entity.architecture.testcase) and
        the current vsim testcase call, i.e. entity(architecture) -gGC_TESTCASE=<testcase>
        """
        self.test_name = test.get_testcase_name()

        # Sequencer built-in testcase
        self.test_call = test.get_gc_str() + " "

        self.test_call += "-lib {} {} ".format(
            test.get_library().get_name(),
            test.get_name(),
        )
        # VHDL architecture
        self.test_call += (
            test.get_arch().get_name() + " "
            if test.get_is_vhdl() is True
            else " "
        )

        self.test_call += " ".join(self.project.settings.get_sim_options())

        self.test_call += self._get_netlist_call()

    def _load_simulator(self, test) -> int:
        """
        This method should be overridden in subclasses to implement
        simulator-specific loading logic.
        """
        self._set_os_environment()
        gui_do_file = self._get_test_path(filename="gui.do", test=test)
        sim_exe = self._get_simulator_executable("vsim")
        command = [sim_exe]
        command += ["-gui"]
        command += ["-do"]
        command += [gui_do_file]
        self.runner = CommandRunner(project=self.project)
        rc = self.runner.gui_run(command=command)
        return int(rc[2])

    @staticmethod
    def _restart_and_run() -> str:
        txt = """
proc rr {} {
    restart; run -all
}
"""
        return txt

    @staticmethod
    def _restart() -> str:
        txt = """
proc rs {} {
    restart
}
"""
        return txt

    def get_sim_path(self) -> str:
        return os.path.join(os_adjust_path(self.project.settings.get_sim_path()), "hdlregression", "library")
    
    def _is_simulator(self, simulator) -> bool:
        return simulator.upper() == self.get_simulator_name()

    def _simulate(self, test) -> str:
        transcript_file = self._get_test_path(filename="transcript", test=test)
        txt = """
proc s {} {
    puts "Running test: %s"
    restart; run -all; transcript file %s
}
""" % (
            self.test_name,
            transcript_file,
        )
        return txt

    def simulate_gui(self) -> None:
        # Get tests to run
        tests = self.testbuilder.get_list_of_tests_to_run()

        # Run tests
        for test in tests:
            # Create unique test output folder
            self._create_test_folder(test.get_test_path())

            self._set_test_specifics(test)
            self._create_gui_do_file(test)

            # Start simulator
            rc = self._load_simulator(test)
            if rc == 2:
                self.logger.info("Test run aborted by user.")
                return None
            elif rc == 1:
                self.logger.warning("Failure running test, aborting.")    


class TclRunnerActiveHDL(TclRunnerRiviera, TclRunnerBase, ActiveHDLRunner):
    """
    A TclRunner specifically for Active-HDL.
    """

    def __init__(self, project=None):
        super().__init__(project)
