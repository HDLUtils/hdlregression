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
import re
from multiprocessing.pool import ThreadPool

from ..hdlfinder import HDLFinder
from .container import Container
from .hdl_modules_pkg import *
from ..report.logger import Logger
from .hdlfile import *


class Library:

    def __init__(self, name, project):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        self.logger.set_level(self.project.settings.get_logger_level())
        self.filename = None
        self.module_list = []

        # Get default library name if not set
        if not name:
            self.lib_name = self.project.settings.get_library_name()
        else:
            self.lib_name = name.lower()

    def get_name(self) -> str:
        return self.lib_name

    def _search_and_return_file_list(self, filename) -> list:
        """
        Search for files and return list for filanames with path.
        """
        # Create a HDLFinder object to locate files if wildcards are used
        filefinder = HDLFinder(filename=filename, project=self.project)
        # Raise a warning if no files were found
        if len(filefinder.get_file_list()) == 0:
            self.logger.warning("Not found: %s" % (filename))
        return filefinder.get_file_list()

    def update_file_list(self) -> None:
        pass

    def check_library_files_for_changes(self) -> None:
        pass

    def prepare_for_run(self) -> None:
        pass

    def get_lib_obj_dep(self) -> list:
        return []

    def get_never_recompile(self) -> bool:
        return True

    def get_compile_order_list(self) -> list:
        return []

    def set_need_compile(self, compile) -> None:
        pass

    def get_need_compile(self) -> bool:
        pass

    def get_hdlfile_list(self) -> list:
        return []

    def get_compile_path(self) -> str:
        pass

    def get_is_precompiled(self) -> bool:
        return False

    def get_lib_dep(self) -> list:
        return []


class PrecompiledLibrary(Library):

    def __init__(self, name, project):
        super().__init__(name=name, project=project)

    def set_compile_path(self, compile_path):
        self.compile_path = compile_path.replace("\\", "/")

    def get_compile_path(self) -> str:
        return self.compile_path

    def set_filename(self, filename):
        self.filename = filename.replace("\\", "/")

    def get_filename(self) -> str:
        return self.filename

    def get_is_precompiled(self) -> bool:
        return True


class HDLLibrary(Library):
    """
    Library class for holding file objects.
    """

    def __init__(self, name=None, project=None):
        super().__init__(name=name, project=project)
        self.no_recompile = False  # never recompile library
        self.lib_dep = []  # library dependencies list
        self.lib_obj_dep_list = []  # list of dependent library objects
        self.lib_hdlfile_compile_order_list = []  # hdlfile compile order list
        self.compile_req = False  # library compilation required
        self.hdlfile_container = Container()  # hdlfile container
        self.temp_hdlfile_container = Container()  # temp storage for add_file()
        # self.netlist_hdlfile_container = Container()  # netlist hdlfile container

    def get_never_recompile(self) -> bool:
        return self.no_recompile

    def set_never_recompile(self, stop_recompile) -> None:
        self.no_recompile = stop_recompile

    def _get_new_hdlfile_obj(
        self,
        file_item,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
        netlist_instance,
    ):
        # VHDL file
        if file_item.lower().endswith(".vhdl") or file_item.lower().endswith(".vhd"):
            return VHDLFile(
                filename_with_path=file_item,
                library=self,
                hdl_version=hdl_version,
                com_options=com_options,
                parse_file=parse_file,
                code_coverage=code_coverage,
                project=self.project,
            )

        # Verilog file
        elif file_item.lower().endswith(".v"):
            return VerilogFile(
                filename_with_path=file_item,
                library=self,
                hdl_version=hdl_version,
                com_options=com_options,
                parse_file=parse_file,
                code_coverage=code_coverage,
                project=self.project,
            )
        elif file_item.lower().endswith(".sdf"):
            return NetlistFile(
                filename_with_path=file_item,
                library=self,
                hdl_version=hdl_version,
                com_options=com_options,
                parse_file=parse_file,
                code_coverage=code_coverage,
                netlist_instance=netlist_instance,
                project=self.project,
            )
        elif file_item.lower().endswith(".sv"):
            return SVFile(
                filename_with_path=file_item,
                library=self,
                hdl_version=hdl_version,
                com_options=com_options,
                parse_file=False,
                code_coverage=code_coverage,
                project=self.project,
            )
        else:
            self.logger.warning("Unknown file type: %s" % (file_item))
            return UnknownFile(
                filename_with_path=file_item,
                library=self,
                hdl_version=hdl_version,
                com_options=com_options,
                parse_file=False,
                code_coverage=code_coverage,
                project=self.project,
            )
        return None

    def add_file(
        self,
        filename,
        hdl_version,
        com_options,
        parse_file,
        code_coverage,
        netlist_instance,
    ) -> None:
        """
        Locates the file and creates a HDLFile object
        that is added to the internal list.
        There is only one HDLFile object per file.

        1. Locate file(s) in a list (warning if not found)
        2. Check if file (with this path) has already been added.
        3. Create a HDLFile object and add it to the hdlfile_container.
        """
        # Iterate list of found files
        for file_item in self._search_and_return_file_list(filename):

            # Check if file is already added
            hdlfile_obj = self.get_hdlfile_obj(file_item)

            # New file?
            if not hdlfile_obj:
                hdlfile_obj = self._get_new_hdlfile_obj(
                    file_item=file_item,
                    hdl_version=hdl_version,
                    com_options=com_options,
                    parse_file=parse_file,
                    netlist_instance=netlist_instance,
                    code_coverage=code_coverage,
                )
                self.logger.debug(
                    "%s add_file(%s) - new file" % (self.get_name(), file_item)
                )

            # Existing file
            else:
                self.logger.debug(
                    "%s add_file(%s) - existing file" % (self.get_name(), file_item)
                )
            self.temp_hdlfile_container.add(hdlfile_obj)

    def remove_file(self, filename) -> bool:
        file_found = False
        for obj in self.hdlfile_container.get():
            if obj.get_filename() == filename:
                self.hdlfile_container.remove(obj)
        for obj in self.temp_hdlfile_container.get():
            if obj.get_filename() == filename:
                self.temp_hdlfile_container.remove(obj)
                file_found = True
        return file_found

    def get_hdlfile_obj(self, filename) -> "HDLFile":
        """
        Returns the file object if found in the file list.
        Returns None if no file object is found.
        """
        # Check with all hdlfile objects in this library (container).
        for hdlfile in self.get_hdlfile_list():
            hdlfile_name = hdlfile.get_filename_with_path()
            if hdlfile_name.lower() == filename.lower():
                return hdlfile

        # Filename not found
        return None

    def update_file_list(self) -> None:
        """
        Update cached file liste with any changes from new run.
        Files that are no longer present in the regression script
        are moved from cache.

        Update library recompilation if necessary.
        """

        def check_list(new_list, old_list) -> tuple:
            new_names = [new_file.get_filename() for new_file in new_list.get()]
            old_names = [old_file.get_filename() for old_file in old_list.get()]

            new_files = [
                hdlfile
                for hdlfile in new_list.get()
                if hdlfile.get_filename() not in old_names
            ]
            removed_files = [
                hdlfile
                for hdlfile in old_list.get()
                if hdlfile.get_filename() not in new_names
            ]
            return (new_files, removed_files)

        # This check is only for regression scripts that call start()
        # multiple times - i.e. no add_files() call, only new regression run.
        if self.temp_hdlfile_container.num_elements() > 0:

            # Get lists of new files and removed files
            (new_files, removed_files) = check_list(
                self.temp_hdlfile_container, self.hdlfile_container
            )

            # Add new files to container
            for new_file in new_files:
                self.hdlfile_container.add(new_file)
                self.logger.debug("Added: %s" % (new_file.get_filename()))
            # Remove removed files from container
            for removed_file in removed_files:
                self.hdlfile_container.remove(removed_file)
                self.logger.debug("Removed: %s" % (removed_file.get_filename()))

            # Updated library recompile when file number has changed.
            if new_files or removed_files:
                self.set_need_compile(True)

            # Empty temporary storage for next regression run.
            self.temp_hdlfile_container.empty_list()

    def check_library_files_for_changes(self) -> None:
        """
        Request each file process/scan file content and
        build module recompile info.
        """

        def devide_list_for_threads(lst, sz):
            return [lst[i : i + sz] for i in range(0, len(lst), sz)]

        def check_if_changed_and_parse(hdlfile) -> None:
            if hdlfile.get_need_compile() is True:
                recompile_needed = hdlfile.parse_file_if_needed()
                if recompile_needed is True:
                    self.set_need_compile(True)
                    for dep_hdlfile in hdlfile.get_hdlfile_dep_on_this():
                        dep_hdlfile.set_need_compile(True)
                else:
                    self.logger.warning(
                        "File was not parsed: %s" % (hdlfile.get_filename_with_path())
                    )

        # Get list of all HDL file objects in this library
        hdlfile_list = self.hdlfile_container.get()
        # Default number of threads
        num_threads = 1
        # Check if threading is enabled, i.e. > 0
        if self.project.settings.get_num_threads() > 0:
            num_threads = len(hdlfile_list)
        # Split the list if we use more than 1 thread
        if num_threads > 1:
            devided_list = devide_list_for_threads(hdlfile_list, num_threads)
            hdlfile_list = []
            for item in devided_list:
                hdlfile_list += item
        # Execute using 1 or more threads
        if num_threads > 0:
            with ThreadPool(processes=num_threads) as thread_pool:
                thread_pool.map(check_if_changed_and_parse, hdlfile_list)

    def get_hdlfile_list(self) -> list:
        return self.hdlfile_container.get()

    def get_compile_order_list(self) -> list:
        return self.lib_hdlfile_compile_order_list

    def set_need_compile(self, compile) -> None:
        """
        Sets the recompile status for the library.
        Will be set if a dependency library need to compile.
        """
        self.compile_req = compile

    def get_need_compile(self) -> bool:
        """
        Returns the recompile status of this library.
        """
        # Library set to never recompile
        if self.no_recompile is True:
            return False
        # Gui request recompile all
        elif self.project.settings.get_gui_compile_all() is True:
            return True
        # Library recompile setting
        else:
            return self.compile_req

    def _get_list_of_lib_modules(self) -> list:
        """
        Returns a list of all modules detected by scanning
        the files in this library.
        """
        module_list = []
        for hdlfile in self.get_hdlfile_list():
            if hdlfile:
                for module in hdlfile.get_modules():
                    module_list.append(module)
        return module_list

    def prepare_for_run(self) -> None:
        """
        Run all necessary steps for compiling this library,
        i.e. scan files, detect dependencies, sort in
        order by dependency.
        """
        # Create list of all modules
        self.module_list = self._get_list_of_lib_modules()

        # Convert module names to module objects in component/configuration modules.
        self._create_module_from_name()

        # Remove non-existing modules
        self._remove_non_existing_modules()
        # Connect modules by dependency and architectures with entities
        self._connect_dep_modules()

        if self.compile_req:
            # Arrange files by dependency
            self._create_list_of_files_in_compile_order()

            # Create a list of other libraries this library depend on.
            self._get_lib_deps_from_modules()

        if self.project.settings.get_debug_mode():
            print(self._present_library())

    def _create_module_from_name(self) -> None:
        """
        Iterate all modules and filters on component/configuration
        modules to extract dependent
        """
        for module in self.module_list:
            if module.get_is_configuration():
                for dep_module in self.module_list:
                    for name in module.get_int_dep_on_this():
                        if re.match(name, dep_module.get_name(), flags=re.IGNORECASE):
                            dep_module.add_int_dep(module.get_name())
                            continue

    def _remove_non_existing_modules(self) -> None:
        """
        Remove all modules created/detected when scanning files,
        which are not real modules (or have not been detected as modules).
        """
        for module in self.module_list:
            for dep_module_name in module.get_int_dep():
                if module.get_type() == "verilog_module":
                    match = any(
                        dep_module
                        for dep_module in self.module_list
                        if dep_module.get_name() == dep_module_name
                    )
                else:
                    match = any(
                        dep_module
                        for dep_module in self.module_list
                        if dep_module.get_name().lower() == dep_module_name
                    )
                if match is False:
                    module.remove_int_dep(dep_module_name)
                    self.logger.debug("Removing unknown module: %s" % (dep_module_name))

    def _connect_dep_modules(self):
        """
        Build connection between modules/packages/instances, i.e.
        each object knows whom it depende on and whom depends on it.
        That is, all modules in all files inside this library are
        dependency connected.
        """
        for update_module in self.module_list:
            update_module_hdlfile = update_module.get_hdlfile()

            for check_module in self.module_list:
                if (update_module == check_module) and (
                    update_module.get_hdlfile() == check_module.get_hdlfile()
                ):
                    continue

                check_module_hdlfile = check_module.get_hdlfile()

                # Connect by detected internal dependency
                if update_module.get_name() in check_module.get_int_dep():
                    check_module.set_this_depend_of(update_module)
                    update_module.set_depend_of_this(check_module)
                    # Update HDLFile objects dependency
                    check_module_hdlfile.add_hdlfile_this_dep_on(update_module_hdlfile)
                    update_module_hdlfile.add_hdlfile_dep_on_this(check_module_hdlfile)

                elif check_module.get_name() in update_module.get_int_dep():
                    update_module.set_this_depend_of(check_module)
                    check_module.set_depend_of_this(update_module)
                    # Update HDLFile objects dependency
                    update_module_hdlfile.add_hdlfile_this_dep_on(check_module_hdlfile)
                    check_module_hdlfile.add_hdlfile_dep_on_this(update_module_hdlfile)

                # ================================================================
                # The following connection do not belong to verilog modules.
                # ================================================================
                if (
                    check_module.get_type() != "verilog_module"
                    and update_module.get_type() != "verilog_module"
                ):
                    # Connect architecture with entity
                    if (
                        check_module.get_is_architecture()
                        and update_module.get_is_entity()
                    ):

                        # Knowledge:
                        # - architecture knows which entity name
                        # - entity do not know which architecture
                        if check_module.get_arch_of() == update_module.get_name():
                            check_module.set_this_depend_of(update_module)
                            update_module.set_depend_of_this(check_module)
                            update_module.add_architecture(check_module)

                    if (
                        update_module.get_is_architecture()
                        and check_module.get_is_entity()
                    ):
                        if update_module.get_arch_of() == check_module.get_name():
                            update_module.set_this_depend_of(check_module)
                            check_module.set_depend_of_this(update_module)
                            check_module.add_architecture(update_module)
                            # Update HDLFile objects dependency
                            update_module_hdlfile.add_hdlfile_this_dep_on(
                                check_module_hdlfile
                            )
                            check_module_hdlfile.add_hdlfile_dep_on_this(
                                update_module_hdlfile
                            )

    def _create_list_of_files_in_compile_order(self):
        """
        Get all modules (arranged in compile order) and add their
        filename to library_hdlfile_compile_order_list.
        Note! Each file is only listed one time.
        Note! The modules have to be arranged in compile order.
        """
        file_list = self.get_hdlfile_list()
        num_files = len(file_list)
        swapped = True
        while swapped:
            swapped = False

            for i in range(num_files):
                # Assume that the first item of the unsorted segment
                # has no dependencies.
                lowest_value_index = i

                self.logger.debug(
                    "Check dep on {}".format(file_list[lowest_value_index].get_name())
                )
                # This loop iterates over the unsorted items
                for j in range(i + 1, num_files):
                    check_file = file_list[j]
                    with_file = file_list[lowest_value_index]

                    if check_file in with_file.get_hdlfile_this_dep_on():
                        if with_file in check_file.get_hdlfile_this_dep_on():
                            if (
                                not check_file.get_filename_with_path()
                                == with_file.get_filename_with_path()
                            ):
                                self.logger.warning(
                                    "{} : recursing dependency {} <-> {}.".format(
                                        self.get_name(),
                                        check_file.get_name(),
                                        with_file.get_name(),
                                    )
                                )
                                continue
                        else:
                            lowest_value_index = j

                # Swap values of the lowest unsorted element with
                # the first unsorted element.
                if i != lowest_value_index:
                    file_list[i], file_list[lowest_value_index] = (
                        file_list[lowest_value_index],
                        file_list[i],
                    )
                    swapped = True

        # Update
        self.lib_hdlfile_compile_order_list = file_list

    def _get_lib_deps_from_modules(self) -> None:
        """
        Check with each module which libraries they depend on.
        """
        for module in self.module_list:
            for library in module.get_ext_dep():
                self.add_lib_dep(library)

    def get_lib_dep(self) -> list:
        """
        Returns:
        lib_dep(list): dependencies for this library.
        """
        return self.lib_dep

    def add_lib_dep(self, library) -> None:
        """
        Method for manually add a library as a dependency.
        """
        if library.lower() not in self.lib_dep:
            self.lib_dep.append(library.lower())

            # Get the HDLLibrary object and save in list
            lib_obj = self.project._get_library_object(
                library.lower(), create_new_if_missing=False
            )
            if lib_obj is not None:
                if lib_obj not in self.lib_obj_dep_list:
                    self.lib_obj_dep_list.append(lib_obj)

    def get_lib_obj_dep(self) -> list:
        return self.lib_obj_dep_list

    def _present_library(self) -> str:
        """
        Printer method for presenting the library w/modules
        in dependency order and w/compile status.
        """
        txt = "\n%s Library %s modules inter-connect %s\n" % (
            "=" * 20,
            self.get_name(),
            "=" * 20,
        )
        for idx, module in enumerate(self.module_list):
            if (
                module.get_is_entity()
                or module.get_is_package()
                or module.get_is_context()
                or module.get_is_new_package()
                or module.get_is_architecture()
                or module.get_is_package_body()
                or (module.get_type() == "verilog_module")
                or module.get_is_configuration()
            ):

                my_dep = ""
                for item in module.get_this_depend_of():
                    my_dep += item.get_name() + "(" + item.get_type() + ")" + ", "

                dep_on_me = ""
                for item in module.get_depend_of_this():
                    dep_on_me += item.get_name() + "(" + item.get_type() + ")" + ", "

                txt += "|-(%d) %s (%s):\n|      ---->:%s\n|      <----:%s\n" % (
                    idx + 1,
                    module.get_name(),
                    module.get_type(),
                    my_dep,
                    dep_on_me,
                )

        txt += "\n%s Library %s files compile order %s\n" % (
            "=" * 20,
            self.get_name(),
            "=" * 20,
        )
        for idx, hdlfile in enumerate(self.lib_hdlfile_compile_order_list):
            tb_str = "(TB)" if hdlfile.get_is_tb() else ""
            txt += "(%d) %s %s\n" % (idx + 1, hdlfile.get_filename_with_path(), tb_str)

        return txt
