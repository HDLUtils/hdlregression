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
import time

from ..scan.vhdlscanner import VHDLScanner
from ..scan.verilogscanner import VerilogScanner


class HDLFile:

    def __init__(
        self,
        filename_with_path,
        project,
        library,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
    ):
        self.project = project
        self.library = library
        self.hdl_version = hdl_version
        self.com_options = com_options
        self.scanner = None
        self.code_coverage = code_coverage

        self.compile_time = 0
        self.hdlfile_this_dep_on_list = []
        self.hdlfile_dep_on_this_list = []

        # Netlist file is not parsed
        self.parse_file = parse_file

        # Setup defaults
        self.file_change_date = os.path.getmtime(filename_with_path)
        # self.filename = None  # Filename with '.vhd'
        self.filename = None
        self.name_from_file = None  # Filename without '.vhd'
        self.filename_with_path = None
        # Get path and filename and update internal information
        self.set_filename(filename_with_path)
        self.com_options = self.set_com_options(com_options=com_options)

    def _get_file_content_as_list(self) -> list:
        """
        Reads the file and returns the content as a list.
        """
        with open(self.filename_with_path, encoding="ISO-8859-1") as read_file:
            file_content_list = read_file.readlines()
        return file_content_list

    def set_library(self, library: str) -> None:
        self.library = library.lower()

    def get_library(self) -> str:
        return self.library

    def update_compile_time(self):
        self.compile_time = time.time()

    def get_need_compile(self) -> bool:
        need_compile = self.get_file_change_date() > self.compile_time
        need_compile = need_compile or self.get_library().get_need_compile()
        return need_compile

    def set_need_compile(self, need_compile: bool):
        """
        Resets the last compile time for this file.
        """
        if need_compile is True:
            self.compile_time = 0

    def get_file_change_date(self) -> str:
        try:
            self.file_change_date = os.path.getmtime(self.get_filename_with_path())
        except:
            self.file_change_date = 0
        finally:
            return self.file_change_date

    def parse_file_if_needed(self) -> bool:
        pass

    def set_filename(self, filename_with_path: str):
        """
        Extract path and filename from file absolute path,
        calculate hash, tokenize and parse file content.
        """
        self.filename_with_path = filename_with_path
        # Sep path and file name
        _, name = os.path.split(filename_with_path)
        self.name_from_file = name[0 : name.find(".")]
        self.filename = name

    def get_filename(self) -> str:
        return self.filename

    def get_filename_with_path(self) -> str:
        return self.filename_with_path

    def get_name(self) -> str:
        return self.name_from_file

    def get_modules(self) -> list:
        """
        Builds and return a list of all modules
        that have been created after scanning the file.
        """
        modules_list = []
        if self.scanner:
            container = self.scanner.get_module_container()
            modules_list = [module for module in container.get()]
        return modules_list

    def get_tb_modules(self) -> list:
        """
        Builds and returns a list of all TB modules
        that have been created after scanning the file.
        """
        modules_list = []
        if self.scanner:
            container = self.scanner.get_module_container()
            modules_list = [module for module in container.get() if module.get_is_tb()]
        return modules_list

    def get_is_tb(self) -> bool:
        """
        Checks all modules created after scanning the file
        and return True if any module is a TB.
        I.e. the file contain a TB.
        """
        return False

    def set_hdl_version(self, hdl_version):
        self.hdl_version = hdl_version

    def get_hdl_version(self) -> str:
        return self.hdl_version

    def set_com_options(self, com_options) -> list:
        """
        Set compile options for file. A check and conversion
        is performed to ensure that the options are passed
        on as a list.

        Params:
          com_options(list): list of file compile options.
        """
        if com_options:
            if not (isinstance(com_options, list)):
                com_options = com_options.strip().replace(",", " ")
                com_options = com_options.split()
        return com_options

    def get_com_options(self) -> str:
        if self.com_options:
            return self.com_options
        else:
            if self.get_is_vhdl() is True:
                return self.project.settings.get_com_options("vhdl")
            else:
                return self.project.settings.get_com_options("verilog")

    def add_hdlfile_this_dep_on(self, hdlfile) -> None:
        """
        Adds a HDLFile which this HDLFile depends on.
        """
        if hdlfile not in self.hdlfile_this_dep_on_list:
            self.hdlfile_this_dep_on_list.append(hdlfile)

    def get_hdlfile_this_dep_on(self) -> list:
        """
        Returns a list of HDLFiles which this HDLFile depends on.
        """
        return self.hdlfile_this_dep_on_list

    def add_hdlfile_dep_on_this(self, hdlfile) -> None:
        """
        Adds a HDLFile that depends on this HDLFile.
        """
        if hdlfile not in self.hdlfile_dep_on_this_list:
            self.hdlfile_dep_on_this_list.append(hdlfile)

    def get_hdlfile_dep_on_this(self) -> None:
        """
        Returns a list of HDLFiles that depends on this HDLFile.
        """
        return self.hdlfile_dep_on_this_list

    def set_code_coverage(self, enabled):
        self.code_coverage = enabled

    def get_code_coverage(self) -> bool:
        return self.code_coverage

    def check_file_type(self, filetype) -> bool:
        return False

    def get_is_verilog(self) -> bool:
        return False

    def get_is_vhdl(self) -> bool:
        return False

    def get_is_netlist(self) -> bool:
        return False

    def _get_com_options(self, simulator) -> str:
        return ""


class VHDLFile(HDLFile):

    def __init__(
        self,
        filename_with_path,
        project,
        library,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
    ):
        super().__init__(
            filename_with_path,
            project,
            library,
            hdl_version,
            com_options,
            parse_file,
            code_coverage,
        )
        self.scanner = VHDLScanner(
            project=self.project,
            library=self.get_library(),
            filename=self.get_filename_with_path(),
            hdlfile=self,
        )        

    def parse_file_if_needed(self) -> bool:
        """
        Read content of file, inspect file and update file content.
        Create a scanner object for the file and scan the content, i.e
        check of TB pragma, find generics and testcases, create module
        objects+++.

        :rtype: bool
        :return: True if file has been parsed, else False
        """
        # Files that should not be parsed are set to False, i.e.
        # return True to caller - caller does not care if file is parsed.
        if self.parse_file is True:
            file_content_list = self._get_file_content_as_list()
            # Extract relevant content from source file
            self.scanner.scan(file_content_list)
        return True

    def _get_com_options(self, simulator) -> str:
        """
        Return a list of compile options for this file.
            Params:
              simulator(str): simulator type name (GHDL, MODELSIM, NVC, ACTICE-HDL, RIVIERA-PRO)

            Returns:
              com_options(str): simulator options for file.
        """
        hdl_version = self.get_hdl_version()
        default_com_options = self.project.settings.get_com_options(hdl_lang="vhdl")

        # User defined hdl_version set
        if simulator.upper() == "GHDL":
            if hdl_version not in ["87", "93", "02", "08"]:
                hdl_version = "08"
            if self.com_options:
                self.com_options = [
                    directive.replace("--std=08", "--std=%s" % (hdl_version))
                    for directive in self.com_options
                ]
            else:
                self.com_options = [
                    directive.replace("--std=08", "--std=%s" % (hdl_version))
                    for directive in default_com_options
                ]

        elif simulator.upper() in ["ACTIVE-HDL", "RIVIERA-PRO"]:
            if not hdl_version:
                hdl_version = "2008"
            if self.com_options:
                self.com_options = [
                    directive.replace("-2008", "-%s" % (hdl_version))
                    for directive in self.com_options
                ]
            else:
                self.com_options = [
                    directive.replace("-2008", "-%s" % (hdl_version))
                    for directive in default_com_options
                ]

        else:
            if not hdl_version:
                hdl_version = "2008"
            if self.com_options:
                self.com_options = [
                    directive.replace("-2008", "-%s" % (hdl_version))
                    for directive in self.com_options
                ]
            else:
                self.com_options = [
                    directive.replace("-2008", "-%s" % (hdl_version))
                    for directive in default_com_options
                ]

        return self.com_options

    def check_file_type(self, filetype) -> bool:
        if filetype.lower() == "vhdl":
            return True
        else:
            return False

    def get_is_vhdl(self) -> bool:
        return True

    def get_is_tb(self) -> bool:
        """
        Checks all modules created after scanning the file
        and return True if any module is a TB.
        I.e. the file contain a TB.
        """
        if self.scanner is not None:
            container = self.scanner.get_module_container()
            for module in container.get():
                if module.get_is_tb():
                    return True
        return False


class NetlistFile(VHDLFile):

    def __init__(
        self,
        filename_with_path,
        project,
        library,
        hdl_version,
        com_options,
        parse_file,
        netlist_instance,
        code_coverage,
    ):
        super().__init__(
            filename_with_path,
            project,
            library,
            hdl_version,
            com_options,
            parse_file,
            code_coverage,
        )
        self.netlist_instance = netlist_instance

    def get_is_netlist(self) -> bool:
        return True

    def parse_file_if_needed(self) -> bool:
        return True

    def get_netlist_instance(self) -> str:
        return self.netlist_instance


class VerilogFile(HDLFile):

    def __init__(
        self,
        filename_with_path,
        project,
        library,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
    ):
        super().__init__(
            filename_with_path,
            project,
            library,
            hdl_version,
            com_options,
            parse_file,
            code_coverage,
        )
        self.scanner = VerilogScanner(
            project=self.project,
            library=self.get_library(),
            filename=self.get_filename_with_path(),
            hdlfile=self,
        )

    def parse_file_if_needed(self) -> bool:
        """
        Read content of file, inspect file and update file content.
        Create a scanner object for the file and scan the content, i.e
        check of TB pragma, find generics and testcases, create module
        objects+++.
        """
        # Check if file should be parsed
        if self.parse_file is True:
            file_content_list = self._get_file_content_as_list()
            # Extract relevant content from source file
            self.scanner.scan(file_content_list)
        return True

    def _get_com_options(self, simulator) -> str:
        """
        Return a list of compile options for this file.
            Params:
              simulator(str): simulator type name (MODELSIM, ACTIVE-HDL, RIVIERA-PRO)

            Returns:
              com_options(str): simulator options for file.
        """
        hdl_version = self.get_hdl_version()
        default_com_options = self.project.settings.get_com_options(hdl_lang="verilog")
        if self.com_options is not None:
            return self.com_options
        else:
            return default_com_options

    def check_file_type(self, filetype) -> bool:
        if filetype.lower() == "verilog":
            return True
        else:
            return False

    def get_is_verilog(self) -> bool:
        return True

    def get_is_tb(self) -> bool:
        """
        Checks all modules created after scanning the file
        and return True if any module is a TB.
        I.e. the file contain a TB.
        """
        if self.scanner is not None:
            container = self.scanner.get_module_container()
            for module in container.get():
                if module.get_is_tb():
                    return True
        return False


class SVFile(HDLFile):

    def __init__(
        self,
        filename_with_path,
        project,
        library,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
    ):
        super().__init__(
            filename_with_path,
            project,
            library,
            hdl_version,
            com_options,
            parse_file,
            code_coverage,
        )

    def check_file_type(self, filetype) -> bool:
        if filetype.lower() == "systemverilog":
            return True
        else:
            return False


class UnknownFile(HDLFile):

    def __init__(
        self,
        filename_with_path,
        project,
        library,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
    ):
        super().__init__(
            filename_with_path,
            project,
            library,
            hdl_version,
            com_options,
            parse_file,
            code_coverage,
        )
