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

import re
from multiprocessing.pool import ThreadPool
from _multiprocessing import flags

from .hdlscanner import HDLScanner
from ..construct.hdl_modules_pkg import EntityModule, ContextModule, ConfigurationModule, ArchitectureModule, PackageModule, PackageBodyModule
from ..report.logger import Logger
from .hdl_regex_pkg import *


class VHDLScanner(HDLScanner):
    '''

    '''

    def __init__(self, project, library, filename, hdlfile):
        super().__init__(project, library, filename, hdlfile)
        self.logger = Logger(name=__name__, project=project)
        self.library_name = self.get_library().get_name().lower()
        self.project = project
        self.logger.set_level(self.project.settings.get_logger_level())

    def get_entity_module(self, name) -> 'EntityModule':
        for module in self.container.get():
            if module.get_is_entity():
                if module.get_name().lower() == name.lower():
                    return module
        # Not found
        module = EntityModule(name=name,
                              library=self.get_library(),
                              logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def get_context_module(self, name) -> 'ContextModule':
        for module in self.container.get():
            if module.get_is_context():
                if module.get_name().lower() == name.lower():
                    return module
        # Not found
        module = ContextModule(name=name,
                               library=self.get_library(),
                               logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def get_configuration_module(self, name) -> 'ConfigurationModule':
        for module in self.container.get():
            if module.get_is_configuration():
                if module.get_name().lower() == name.lower():
                    return module
        # Not found
        module = ConfigurationModule(name=name,
                                     library=self.get_library(),
                                     logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def get_architecture_module(self, name, arch_of_name) -> 'ArchitectureModule':
        for module in self.container.get():
            if module.get_is_architecture():
                if module.get_name().lower() == name.lower():
                    return module
        # Not found
        module = ArchitectureModule(name=name,
                                    arch_of=arch_of_name,
                                    library=self.get_library(),
                                    logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def get_package_module(self, name) -> 'PackageModule':
        for module in self.container.get():
            if module.get_is_package():
                if module.get_name().lower() == name.lower():
                    return module
        # Not found
        module = PackageModule(name=name,
                               library=self.get_library(),
                               logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def get_package_body_module(self, name) -> 'PackageBodyModule':
        for module in self.container.get():
            if module.get_is_package_body():
                if module.get_name().lower() == name.lower():
                    return module
        # Not found
        module = PackageBodyModule(name=name,
                                   library=self.get_library(),
                                   logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def tokenize(self, file_content_list):
        '''
        Scan code for dependencies and modules.
        '''

        def devide_list_for_threads(lst, sz): return [
            lst[i:i + sz] for i in range(0, len(lst), sz)]

        code = ' '.join(map(str, file_content_list))

        # Helper method for executing code parsing.
        def run_parser(parser):
            parser._parse(code)

        # Need to run library parser prior to building
        # any other module
        lib_parser = LibraryParser(master=self)
        lib_parser._parse(code)

        # Setup remaining parsers
        parsers = []
        parsers.append(EntityParser(master=self))
        parsers.append(ConfigurationParser(master=self))
        parsers.append(ContextParser(master=self))
        parsers.append(ArchitectureParser(master=self))
        parsers.append(PackageParser(master=self))

        # Default number of threads
        num_threads = 1
        # Adjust to one thread per parser if threading is enabled
        if self.project.settings.get_num_threads() > 0:
            num_threads = len(parsers)
        # Split the list if we use more than 1 thread
        if num_threads > 1:
            devided_list = devide_list_for_threads(parsers, num_threads)
            parsers = []
            for item in devided_list:
                parsers += item
        # Execute using 1 or more threads
        with ThreadPool(num_threads) as thread_pool:
            thread_pool.map(run_parser, parsers)

        # Finalize module on end of file if not already done
        for module in self.get_module_container().get():
            if not module.get_complete():
                self.logger.debug("Module %s was not finalized." % 
                                  (module.get_name()))
                module.set_complete()

    # ================================================
    # Pre-processing methods
    # ================================================

    def _check_for_pragmas(self, line) -> bool:
        '''
        Check if line has the testbench pragma and
        set the is_tb variable if found.
        '''
        # Check for testbench pragma
        if re.search(RE_VHDL_TB, line):
            return True
        return False

    #
    # Cleaning methods - called from parent
    #
    # 1. empty out strings
    # 2  locate TB pragma
    # 3. remove comments
    # 4. combine lines, should end wit ";"
    #
    def _clean_code(self, file_content_list) -> list:
        '''
        Pre-cleaning code to ease tokenizing afterwards:
         - 1 - check for pragmas
         - 2 - remove comments (regular and block)
         - 3 - remove all strings
        '''
        res = []
        in_block_comment = False
        append_line = None
        for line in file_content_list:
            line = line.strip()

            if append_line is None:
                append_line = line
            else:
                append_line += ' ' + line

            if not in_block_comment:

                # check for hdlregression pragmas
                if self._check_for_pragmas(append_line) is True:
                    append_line += append_line + ';'

                # clear content in strings on this line, except testcases
                if not re.search(self.testcase_string, append_line, flags=re.IGNORECASE):
                    append_line = re.sub(
                        '".*?"', '""', append_line, flags=re.IGNORECASE)

                # remove comments line, except TB pragma
                if not re.search(RE_VHDL_TB, append_line.lower()):
                    append_line = re.sub(RE_VHDL_COMMENT_LINE, '', append_line)

                # check if the block comment starts on this line
                if re.findall(RE_VHDL_COMMENT_BLOCK_START_LINE, append_line):

                    # check if block comment also finishes on this line
                    if re.findall(RE_VHDL_COMMENT_BLOCK_START, append_line) and re.findall(RE_VHDL_COMMENT_BLOCK_END, append_line):
                        self.logger.debug(
                            '[BC_START_COMPLETE] %s' % (append_line))
                        in_block_comment = False
                        append_line = re.sub(
                            RE_VHDL_COMMENT_BLOCK_START_LINE + RE_VHDL_COMMENT_BLOCK_END, '', append_line)
                    else:
                        self.logger.debug('[BC_START] %s' % (append_line))
                        in_block_comment = True
                        append_line = re.sub(
                            RE_VHDL_COMMENT_BLOCK_START_LINE, '', append_line)

            elif in_block_comment:
                # check if the block comment ends on this line
                if re.findall(RE_VHDL_COMMENT_BLOCK_END, append_line):
                    self.logger.debug('[BC_END] %s' % (append_line))
                    in_block_comment = False
                    append_line = re.sub(
                        RE_VHDL_COMMENT_BLOCK_END_LINE, '', append_line)

                # still in a block comment -> empty the line
                else:
                    append_line = ''

            if re.search(r';', append_line, flags=re.IGNORECASE):
                res.append(append_line)
                append_line = None

        return res


class BaseParser:

    # regex flags
    _ALL_FLAGS = re.IGNORECASE | re.MULTILINE | re.DOTALL | re.VERBOSE

    def __init__(self, master):
        self.master = master
        self.module = None
        self.library_name = self.master.get_library().get_name()

    def _lib_match(self, library):
        # Check with current library
        library_match = re.match(r'%s|work' % self.library_name,
                                 library,
                                 flags=re.IGNORECASE)
        return library_match

    def _alias_reference(self, code):
        # alias AliasName [: DataType] is Name [Signature];
        re_alias = re.compile(r'''
                \balias
                \s+[a-zA-Z_0-9]+            # alias name
                (\s*\:\s*[a-zA-Z_\.0-9]+)?  # datatype
                \s+is
                \s+(?P<name>[a-zA-Z_\.0-9]+) # name
                (\s+[a-zA-Z_\.0-9]+)?       # signature
                \s*;
        ''', flags=self._ALL_FLAGS)

        for match in re.finditer(re_alias, code):
            alias_name = match.group('name')

            if '.' in alias_name:
                alias_name = alias_name.split('.')
                library = alias_name[0]
                module = alias_name[1]

                # Module in same library
                if self._lib_match(library):  # library
                    self.module.add_int_dep(module)
                # Different library
                else:
                    self.module.add_ext_dep(library)


class LibraryParser(BaseParser):
    '''
    Extract library dependencies and
    module/use dependencies.
    '''

    def _parse(self, code):
        # Match library clauses
        re_lib = re.compile(r'''
                            \blibrary
                            \s+(?P<library>[a-zA-Z_,0-9\s*]+)
                            \s*;
                            ''',
                            flags=self._ALL_FLAGS)

        matches = re.finditer(re_lib, code)

        for match in matches:
            library = match.group('library')
            if library:
                self.master.add_library_dep(library)
        self._parse_use(code)
        self._parse_context(code)

    def _parse_use(self, code):
        # Match use clauses
        re_use = re.compile(r'\buse\s+(?P<use>[a-zA-Z_\.0-9]+);',
                            flags=self._ALL_FLAGS)

        matches = re.finditer(re_use, code)
        for match in matches:
            use_clause = str(match.group('use'))

            library = re.search(r'\b\w+\.', use_clause)
            library = library.group().replace('.', '')
            # Check with current library
            library_match = re.match(r'%s|work' % self.library_name,
                                     library,
                                     flags=re.IGNORECASE)
            if library_match:
                use = re.sub(r'\b(work|%s)' % self.library_name, '', use_clause,
                             count=1, flags=re.IGNORECASE)
                use_list = use.split('.')
                use = list(filter(None, use_list))[0]
                self.master.add_int_dep(use)

    def _parse_context(self, code):
        # Match context clause from beginning of line
        re_context = re.compile(r'\b\s*(?P<pre>[a-zA-Z_\.0-9]+\s+)?context\s+(?P<use>[a-zA-Z_\.0-9]+);',
                                flags=self._ALL_FLAGS)

        matches = re.finditer(re_context, code)
        for match in matches:
            pre_match = str(match.group('pre'))
            use_clause = str(match.group('use'))

            # catch any actual context file            
            if pre_match:
                if re.match(r'end', pre_match, flags=re.IGNORECASE):
                    continue

            library = re.search(r'\b\w+\.', use_clause)
            library = library.group().replace('.', '')
            # Check with current library
            library_match = re.match(r'%s|work' % self.library_name,
                                     library,
                                     flags=re.IGNORECASE)
            if library_match:
                use = re.sub(r'\b(work|%s)' % self.library_name, '', use_clause,
                             count=1, flags=re.IGNORECASE)
                use_list = use.split('.')
                use = list(filter(None, use_list))[0]
                self.master.add_int_dep(use)


class ContextParser(BaseParser):
    '''
    Extract context modules with dependencies.
    '''

    def _parse(self, code):
        re_start = re.compile(r'''
                            \bcontext
                            \s+(?P<context_name>[a-zA-Z_0-9]+)
                            \s+is
        ''', flags=self._ALL_FLAGS)

        re_end = re.compile(r'''
                            \bend
                            (\s+context)?
                            (\s+[a-zA-Z0-0\_]*)?
                            \s*;
        ''', flags=self._ALL_FLAGS)

        start_matches = re.finditer(re_start, code)

        for start_match in start_matches:
            end_match = re_end.search(code, start_match.end())

            name = start_match.group('context_name')
            self.module = self.master.get_context_module(name)
            if end_match:
                self._parse_dependencies(code[start_match.end():end_match.start()])
            else:
                print('Unable to detect context end.')

    def _parse_dependencies(self, code):
        re_dep = re.compile(r'''
            (\blibrary\s+(?P<library>\w+);)
            |
            (\buse\s+(?P<use>[a-zA-Z_\.0-9]+);)
            ''',
                            flags=self._ALL_FLAGS)

        matches = re.finditer(re_dep, code)
        for match in matches:
            library = match.group('library')
            use_clause = match.group('use')
            if library:
                # Check with current library
                library_match = self._lib_match(library)

                # Different library
                if not library_match:
                    self.module.add_ext_dep(library)

            if use_clause:
                library = re.search(r'\b\w+\.', use_clause)
                library = library.group().replace('.', '')

                # Check with current library - only add modules from own library
                library_match = self._lib_match(library)
                if library_match:
                    use = re.sub(r'\b(work|%s)\.' % self.library_name, '', use_clause,
                                 count=1, flags=re.IGNORECASE)
                    use_list = use.split('.')
                    use = list(filter(None, use_list))[0]
                    self.module.add_int_dep(use)


class ConfigurationParser(BaseParser):
    '''
    Exatract configuration modules with
    dependencies.
    '''

    def _parse(self, code):
        # Match: configuration <nn> of <nn> is
        re_start = re.compile(r'''
                                \bconfiguration
                                \s+(?P<config_name>\w+)
                                \s+of
                                \s+(?P<config_of>\w+)
                                \s+is
                                \s+
                                ''', flags=self._ALL_FLAGS)

        # Match: end [configuration] [<nn>];   -- exclude "end for;"
        re_end = re.compile(r'''
                            \bend
                            (\s+configuration)?
                            (?!\s+for\s*;)
                            (\s+\w+)?
                            \s*;
                            ''', flags=self._ALL_FLAGS)

        start_matches = re.finditer(re_start, code)

        for start_match in start_matches:
            end_match = re_end.search(code, start_match.end())

            name = start_match.group('config_name')
            self.module = self.master.get_configuration_module(name)
            self.module.add_int_dep(start_match.group('config_of'))
            self._parse_dependencies(code[start_match.end():end_match.start()])

    def _parse_dependencies(self, code):
        # Match "for all:", "for" and "use entity"
        re_dep = re.compile(r'''
                            ((\bfor\s+(all\s*:\s*)?)|(\buse\s+entity\s+))
                            (?P<name>[a-zA-Z_0-9\(\)\.]+)
                            ''', flags=self._ALL_FLAGS)

        # Match dependency
        re_dep_mod = re.compile(r'''
                                (?P<library>[a-zA-Z_0-9]+\.)?
                                (?P<entity>[a-zA-Z_0-9]+)
                                (?P<arch>\([a-zA-Z_0-9]+\))?
        ''', flags=re.IGNORECASE | re.VERBOSE | re.DOTALL)

        matches = re.finditer(re_dep, code)
        for match in matches:
            item = match.group('name')
            dependency = re.match(re_dep_mod, item)

            library = dependency.group('library')

            if library is not None:
                library = str(library)
                library_match = re.match(r'%s|work' % self.module.get_library().get_name(),
                                         library,
                                         flags=re.IGNORECASE)
                if not library_match:
                    library = library.replace('.', '')
                    self.module.add_ext_dep(library)

            entity = dependency.group('entity')
            self.module.add_int_dep(entity)

            arch = dependency.group('arch')
            if arch:
                arch = arch.replace('(', '').replace(')', '')
                # Check if same library
                self.module.add_int_dep(arch)


class EntityParser(BaseParser):
    '''
    Extract entity modules and generics.
    '''

    def _parse(self, code):
        # testbench pragma
        re_tb = re.compile(r'\s*--\s*hdlregression\s*:\s*tb\s*',
                           flags=self._ALL_FLAGS)
        # entity definition start
        re_start = re.compile(r'''
                        \bentity
                        \s+
                        (?P<name>\w+)
                        \s+
                        is\s+''', flags=self._ALL_FLAGS)
        # entity definition end
        re_end = re.compile(r'''
                        (\b|\s*)
                        end
                        (\s+[a-zA-Z_0-9]+)? # entity/entity_name
                        (\s+[a-zA-Z_0-9]+)? # entity/entity_name
                        \s*;''', flags=self._ALL_FLAGS)

        start_matches = re.finditer(re_start, code)

        for start_match in start_matches:
            is_tb = re.search(re_tb, code[:start_match.start()])
            entity_name = start_match.group('name')
            end_match = re_end.search(code, start_match.end())

            self.module = self.master.get_entity_module(name=entity_name)
            self.module.add_int_dep(self.master.get_int_dep())
            self.module.add_ext_dep(self.master.get_library_dep())
            if is_tb:
                self.module.set_is_tb()
            if end_match:
                code = code[start_match.end():end_match.start()]
                self._generics(code)

    def _generics(self, code):
        '''
        Extract entity generics.
        '''
        gc_start = re.search(
            r'(\b|\s+)generic\s*\(', code, flags=self._ALL_FLAGS)
        if gc_start:
            code = code[gc_start.end():]

            matches = re.finditer(r'''
                            \b
                            (?P<name>\w+)
                            \s*\:\s*
                            (?P<type>[a-zA-Z_\-\(\)\.]+)
                            ''', code, flags=self._ALL_FLAGS)

            for match in matches:
                if match.group('type').lower() not in ['in', 'out', 'inout', 'buffer' 'linkage']:
                    self.module.add_generic(match.group('name'))


class ArchitectureParser(BaseParser):
    '''
    Extract architecture modules and
    run the TestcaseParser inside relevant code section.
    '''

    def _parse(self, code):
        re_arch = re.compile(r'''
                    \b
                    architecture
                    \s+
                    (?P<name>\w+)
                    \s+
                    of
                    \s+
                    (?P<entity>\w+)
                    \s+
                    is
                    ''', flags=self._ALL_FLAGS)

        matches = re.finditer(re_arch, code)
        search_code = None
        for match in matches:

            self.module = self.master.get_architecture_module(name=match.group('name'),
                                                              arch_of_name=match.group('entity'))
            self.module.add_int_dep(self.master.get_int_dep())
            self.module.add_ext_dep(self.master.get_library_dep())
            self.module.add_int_dep(match.group('entity'))

            # Parse sub section of code only once
            # NOTE! Multiple architectures inside one file is legal, i.e.
            #       can lead to problems when detecting testcases.
            if search_code is None:
                search_code = code[match.end():]
                # Parse sequencer testcases
                testcase_parser = TestcaseParser(master=self.master)
                testcase_parser._parse(search_code)
                # Parse instantiations
                self._instantiation_parse(search_code)

            # Add sequencer testcases to module
            for testcase in self.master.get_testcase():
                self.module.add_testcase(testcase)

    def _instantiation_parse(self, code):
        # Parse instantiations in architecture part
        self._entity_instantiation(code)
        self._configuration_instantiation(code)
        self._alias_reference(code)

    def _entity_instantiation(self, code):
        # Entity instantiations
        re_entity = re.compile(r'''
                        \b\w+                           # label
                        \s*\:\s*entity                  # : entity keyword
                        \s+(?P<name>[a-zA-Z_0-9\.]+)    # entity name
                        (\s*\((?P<arch>\w+)\))?         # possible (architecture)
                        #((\s*\((?P<arch>\w+)\)\s+)|\s*)
                        (\s+|\s*;)                      # whitespace
                        ''',
                               flags=self._ALL_FLAGS)

        for match in re.finditer(re_entity, code):
            inst_name = match.group('name')

            # With library
            if '.' in inst_name:
                inst_name = inst_name.split('.')
                library = inst_name[0]
                module = inst_name[1]

                # Module in same library
                if self._lib_match(library):
                    self.module.add_int_dep(module)
                # Different library
                else:
                    self.module.add_ext_dep(library)
            # Without library
            else:
                self.module.add_int_dep(inst_name)

    def _configuration_instantiation(self, code):
        # Configuration instantiations
        re_configuration = re.compile(r'''
                        \b\w+
                        \s*\:\s*configuration
                        \s+(?P<name>[a-zA-Z_0-9\.]+)
                        \s+
                        ''', flags=self._ALL_FLAGS)
        for match in re.finditer(re_configuration, code):
            conf_name = match.group('name')

            # With library
            if '.' in conf_name:
                conf_name = conf_name.split('.')
                library = conf_name[0]
                configuration = conf_name[1]

                # Module in same library
                if self._lib_match(library):
                    self.module.add_int_dep(configuration)
                # Different library
                else:
                    self.module.add_ext_dep(library)
            # Without library
            else:
                self.module.add_int_dep(conf_name)


class TestcaseParser(BaseParser):
    '''
    Extract testcase defines from testbench sequencer,
    run from ArchitectureParser.
    '''

    def _parse(self, code):
        # Match testcases
        re_tc = re.compile(r'''
                            \s+
                            (\(\s*)?                                    # possible bracket start
                            %s\s*                                       # testcase generic string
                            =
                            \s*\"(?P<testcase>[a-zA-Z_\-0-9]+)\"\s*     # testcase name
                            (\)\s*)?                                    # possible bracket end
        ''' % self.master.testcase_string, flags=self._ALL_FLAGS)

        matches = re.finditer(re_tc, code)
        for match in matches:
            self.master.add_testcase(str(match.group('testcase')))


class PackageParser(BaseParser):
    '''
    Extract package modules.
    '''

    def _parse(self, code):
        # Package declaration, excluding new instances
        re_package_dec = re.compile(r'''
                    \bpackage
                    \s+(?P<name_dec>\w+)
                    \s+is
                    \s+
                     (?!\s+new\s+)
        ''', flags=self._ALL_FLAGS)

        # Package body
        re_package_bdy = re.compile(r'''
                    \bpackage
                    \s+body
                    \s+(?P<name_bdy>\w+)
                    \s+is
                    \s+
        ''', flags=self._ALL_FLAGS)

        # Package declaration section
        for match in re.finditer(re_package_dec, code):
            pkg_name = match.group('name_dec').lower()
            # if pkg_name not in pkg_list:
            self.module = self.master.get_package_module(name=pkg_name)
            self.module.add_int_dep(self.master.get_int_dep())
            self.module.add_ext_dep(self.master.get_library_dep())
            pkg_module = self.module

            self._alias_reference(code[match.end():])

            new_pkg_list = self._new_package_inst(code[match.end():])
            for new_pkg_module in new_pkg_list:
                pkg_module.add_int_dep(new_pkg_module.get_name())

        # Package body section
        for match in re.finditer(re_package_bdy, code):
            pkg_name = match.group('name_bdy').lower()

            self.module = self.master.get_package_body_module(name=pkg_name)
            self.module.add_int_dep(pkg_name)
            self.module.add_int_dep(self.master.get_int_dep())
            self.module.add_ext_dep(self.master.get_library_dep())
            pkg_body_module = self.module

            self._alias_reference(code[match.end():])

            new_pkg_list = self._new_package_inst(code[match.end():])
            for new_pkg_module in new_pkg_list:
                pkg_body_module.add_int_dep(new_pkg_module.get_name())

        # Search for new package instances
        self._new_package_inst(code)

    def _new_package_inst(self, code) -> list:
        # New package instantiation
        _RE_NEW_PACKAGE = re.compile(r'''
            \bpackage
            \s+
            (?P<new_pkg_name>[a-zA-Z_0-9]+)
            \s+is
            \s+new
            \s+
            (?P<library>[a-zA-Z_0-9]+)
            \.
            (?P<name>[a-zA-Z_0-9]+)
            \s+
        ''', flags=self._ALL_FLAGS)

        modules = []

        # New package instantiations
        for match in re.finditer(_RE_NEW_PACKAGE, code):
            new_pkg = match.group('new_pkg_name')
            library = match.group('library')
            package = match.group('name')

            self.module = self.master.get_package_module(name=new_pkg)
            # Module in same library
            if self._lib_match(library):
                self.module.add_int_dep(package)
                self.module.add_int_dep(self.master.get_int_dep())
                self.module.add_ext_dep(self.master.get_library_dep())
                modules.append(self.module)

            # Different library
            else:
                self.module.add_ext_dep(library)

        return modules
