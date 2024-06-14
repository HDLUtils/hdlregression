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


class BaseModule:

    def __init__(self, logger):
        self.logger = logger
        self.name = None
        self.library = None
        self.type = None
        self.is_tb = False
        self.complete = False
        self.hdlfile = None
        self.filename = None
        # Lists
        self.int_dep_on_this_list = []
        self.int_dep_list = []
        self.ext_dep_list = []
        self.this_depend_of_list = []
        self.depent_of_this_list = []

    def set_hdlfile(self, hdlfile):
        self.hdlfile = hdlfile
        self.logger.debug(
            "[%s] file=%s" % (self.get_name(), self.hdlfile.get_filename_with_path())
        )

    def get_hdlfile(self) -> "HDLFile":
        return self.hdlfile

    def set_name(self, name):
        self.name = name.lower()

    def get_name(self) -> str:
        return self.name

    def set_type(self, type):
        self.type = type.lower()
        self.logger.debug("[%s] type=%s" % (self.get_name(), self.type))

    def get_type(self) -> str:
        return self.type

    def set_library(self, library):
        self.library = library
        self.logger.debug(
            "[%s] library=%s" % (self.get_name(), self.library.get_name())
        )

    def get_library(self) -> str:
        return self.library

    def set_filename(self, filename):
        self.filename = filename

    def get_filename(self) -> str:
        return self.filename

    def set_need_compile(self, need_compile):
        self.hdlfile.set_need_compile(need_compile)

    def get_need_compile(self) -> bool:
        return self.hdlfile.get_need_compile()

    def get_architecture(self) -> list:
        return []

    def add_int_dep(self, dep_name_list):
        if isinstance(dep_name_list, list):
            for item in dep_name_list:
                item_name = item.lower()
                if not (item_name in self.int_dep_list):
                    self.int_dep_list.append(item_name)
                    self.logger.debug("[%s] int_dep=%s" % (self.get_name(), item_name))
        else:
            dep_name = dep_name_list.lower()
            if not (dep_name in self.int_dep_list):
                self.int_dep_list.append(dep_name)
                self.logger.debug("[%s] int_dep=%s" % (self.get_name(), dep_name))

    def get_int_dep(self) -> list:
        return self.int_dep_list

    def get_int_dep_on_this(self) -> list:
        """
        Returns a list of module names that depend on
        this module.
        """
        return self.int_dep_on_this_list

    def remove_int_dep(self, module_name) -> None:
        if self.get_is_verilog_module() is False:
            module_name = module_name.lower()
        self.int_dep_list.remove(module_name)

    def add_ext_dep(self, dep):
        if isinstance(dep, list):
            for item in dep:
                item_name = item.lower()
                if not (item_name in self.ext_dep_list):
                    self.ext_dep_list.append(item_name)
                    self.logger.debug("[%s] ext_dep=%s" % (self.get_name(), item_name))
        else:
            dep_name = dep.lower()
            if not (dep_name in self.ext_dep_list):
                self.ext_dep_list.append(dep_name)
                self.logger.debug("[%s] ext_dep=%s" % (self.get_name(), dep_name))

    def get_ext_dep(self) -> list:
        return self.ext_dep_list

    def set_complete(self, complete=True):
        self.complete = complete
        self.logger.debug("[%s] complete=%s" % (self.get_name(), complete))

    def get_complete(self) -> bool:
        return self.complete

    def set_depend_of_this(self, dep):
        if not (dep in self.depent_of_this_list):
            self.depent_of_this_list.append(dep)

    def get_depend_of_this(self) -> list:
        return self.depent_of_this_list

    def set_this_depend_of(self, dep):
        if not (dep in self.this_depend_of_list):
            self.this_depend_of_list.append(dep)

    def get_this_depend_of(self) -> list:
        return self.this_depend_of_list

    def set_is_tb(self):
        self.is_tb = True

    def get_is_tb(self) -> bool:
        return self.is_tb

    def get_is_entity(self) -> bool:
        return self.get_type() == "entity"

    def get_is_context(self) -> bool:
        return self.get_type() == "context"

    def get_is_package(self) -> bool:
        return self.get_type() == "package"

    def get_is_package_body(self) -> bool:
        return self.get_type() == "package_body"

    def get_is_architecture(self) -> bool:
        return self.get_type() == "architecture"

    def get_is_new_package(self) -> bool:
        return self.get_type() == "new_package"

    def get_is_configuration(self) -> bool:
        return self.get_type() == "configuration"

    def get_is_verilog_module(self) -> bool:
        return self.get_type() == "verilog_module"


class EntityModule(BaseModule):
    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("entity")
        super().set_library(library)
        self.arch_list = []
        self.generic_list = []

    def add_generic(self, generic):
        generic = generic.lower().replace(" ", "")
        if not (generic in self.generic_list):
            self.generic_list.append(generic)

    def get_generic(self) -> list:
        return self.generic_list

    def add_architecture(self, arch):
        if not (arch in self.arch_list):
            self.arch_list.append(arch)

    def get_architecture(self) -> list:
        return self.arch_list

    def get_type(self) -> str:
        return "entity"


class PackageModule(BaseModule):

    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("package")
        super().set_library(library)

    def get_type(self) -> str:
        return "package"


class PackageBodyModule(BaseModule):

    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("package_body")
        super().set_library(library)

    def get_type(self) -> str:
        return "package_body"


class NewPackageModule(BaseModule):

    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("new_package")
        super().set_library(library)

    def get_type(self) -> str:
        return "package"


class ContextModule(BaseModule):

    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("context")
        super().set_library(library)

    def get_type(self) -> str:
        return "context"


class ConfigurationModule(BaseModule):

    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("configuration")
        super().set_library(library)

    def get_type(self) -> str:
        return "configuration"


class ArchitectureModule(BaseModule):

    def __init__(self, name, arch_of, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("architecture")
        super().set_library(library)
        self.set_arch_of(arch_of)
        self.testcase_list = []
        self.logger.debug("[%s] arch_of=%s" % (self.get_name(), self.get_arch_of()))

    def set_arch_of(self, arch_of) -> str:
        self.arch_of = arch_of.lower()

    def get_arch_of(self) -> str:
        return self.arch_of

    def add_testcase(self, testcase):
        if testcase not in self.testcase_list:
            self.testcase_list.append(testcase)
            self.logger.debug("[%s] testcase=%s" % (self.get_name(), testcase))

    def get_testcase(self) -> list:
        return self.testcase_list

    def get_has_testcase(self) -> bool:
        return len(self.testcase_list) > 0

    def get_type(self) -> str:
        return "architecture"


# ================================================
# Verilog
# ================================================


class VerilogModule(BaseModule):

    def __init__(self, name, library, logger):
        super().__init__(logger)
        super().set_name(name)
        super().set_type("verilog_module")
        super().set_library(library)
        self.parameter_list = []
        self.testcase_list = []

    def add_parameter(self, parameter):
        parameter = parameter.replace(" ", "")
        if parameter not in self.parameter_list:
            self.parameter_list.append(parameter)

    def get_parameter(self) -> list:
        return self.parameter_list

    def get_type(self) -> str:
        return "verilog_module"

    def add_int_dep(self, dep):
        if isinstance(dep, list):
            for item in dep:
                item_name = item
                if not (item_name in self.int_dep_list):
                    self.int_dep_list.append(item_name)
                    self.logger.debug("[%s] int_dep=%s" % (self.get_name(), item_name))
        else:
            dep_name = dep
            if dep_name not in self.int_dep_list:
                self.int_dep_list.append(dep_name)
                self.logger.debug("[%s] int_dep=%s" % (self.get_name(), dep_name))

    def get_int_dep(self) -> list:
        return self.int_dep_list

    def add_testcase(self, testcase):
        if testcase not in self.testcase_list:
            self.testcase_list.append(testcase)
            self.logger.debug("[%s] testcase=%s" % (self.get_name(), testcase))

    def get_testcase(self) -> list:
        return self.testcase_list

    def get_has_testcase(self) -> bool:
        return len(self.testcase_list) > 0
