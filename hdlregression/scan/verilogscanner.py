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


from multiprocessing.pool import ThreadPool

if __package__ is None or __package__ == '':
    from hdlscanner import HDLScanner
    from hdl_modules_pkg import VerilogModule
    from logger import Logger
    from hdl_regex_pkg import *
else:
    from .hdlscanner import HDLScanner
    from ..struct.hdl_modules_pkg import VerilogModule
    from ..report.logger import Logger
    from .hdl_regex_pkg import *


class VerilogScanner(HDLScanner):
    '''

    '''

    def __init__(self, project, library, filename, hdlfile):
        super().__init__(project, library, filename, hdlfile)
        self.logger = Logger(name=__name__, project=project)
        self.library_name = self.get_library().get_name().lower()
        self.project = project
        self.logger.set_level(self.project.settings.get_logger_level())

    def get_verilog_module(self, name) -> VerilogModule:
        for module in self.container.get():
            if module.get_is_verilog_module():
                if module.get_name() == name:
                    return module
        # Not found
        module = VerilogModule(name=name,
                               library=self.get_library(),
                               logger=self.logger)
        module.set_filename(self.get_filename())
        self.add_module_to_container(module)
        return module

    def tokenize(self, file_content_list):
        '''
        Scan code for dependencies and modules.
        '''
        code = ' '.join(map(str, file_content_list))

        # Helper method for executing code parsing.
        def run_parser(parser):
            parser._parse(code)

        parsers = []
        parsers.append(ModuleParser(master=self))

        if self.project.settings.get_threading() is True:
            thread_pool = ThreadPool(processes=len(parsers))
            thread_pool.map(run_parser, parsers)
            thread_pool.close()
        else:
            for parser in parsers:
                parser._parse(code)

        # Finalize module on end of file if not already done
        for module in self.get_module_container().get():
            if not module.get_complete():
                self.logger.debug("Module %s was not finalized." %
                                  (module.get_name()))
                module.set_complete()

        return

    # ================================================
    #  Pre-processing methods
    # ================================================
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
        is_tb = False
        for line in file_content_list:
            line = line.strip()

            if append_line is None:
                append_line = line
            else:
                append_line += ' ' + line

            if not in_block_comment:

                # clear content in strings on this line, except testcases
                if not re.search(self.testcase_string, append_line, flags=re.IGNORECASE):
                    append_line = re.sub(
                        '".*?"', '""', append_line, flags=re.IGNORECASE)

                # check for hdlregression pragmas
                if re.search(RE_VERILOG_TB, append_line) and is_tb is False:
                    is_tb = True
                    append_line += append_line + ' '

                # remove comments line, except TB pragma
                elif re.search(RE_VERILOG_COMMENT_LINE, append_line):
                    append_line = re.sub(
                        RE_VERILOG_COMMENT_LINE, '', append_line)

                # check if the block comment starts on this line
                if re.findall(RE_VERILOG_COMMENT_BLOCK_START, append_line):

                    # check if block comment also finishes on this line
                    if re.findall(RE_VERILOG_COMMENT_BLOCK_START, append_line) and re.findall(RE_VERILOG_COMMENT_BLOCK_END, append_line):
                        self.logger.debug(
                            '[BC_START_COMPLETE] %s' % (append_line))
                        in_block_comment = False
                        append_line = re.sub(r'/\*.*\*/', '', append_line)

                    else:
                        self.logger.debug('[BC_START] %s' % (line))
                        in_block_comment = True
                        append_line = re.sub(
                            RE_VERILOG_COMMENT_BLOCK_START_LINE, '', append_line)

            elif in_block_comment:
                # check if the block comment ends on this line
                if re.findall(RE_VERILOG_COMMENT_BLOCK_END, append_line):
                    self.logger.debug('[BC_END] %s' % (append_line))
                    in_block_comment = False
                    append_line = re.sub(
                        RE_VERILOG_COMMENT_BLOCK_END_LINE, '', append_line)

                # still in a block comment -> empty the line
                else:
                    append_line = ''

            if re.search(r'\bend[a-zA-Z_0-9]+', append_line, flags=re.IGNORECASE) or is_tb is True:
                res.append(append_line)
                append_line = None
                is_tb = False

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
        library_match = re.match(r'%s' % self.library_name,
                                 library,
                                 flags=re.IGNORECASE)
        return library_match


class ModuleParser(BaseParser):

    def _parse(self, code):
        # testbench pragma
        re_tb = re.compile(r'//\s*hdlregression\s*:\s*tb\s*', flags=self._ALL_FLAGS)
        # match module
        re_module_start = re.compile(r'''
                                      \bmodule
                                      \s+(?P<name>[a-zA-Z_0-9]+)
                                      (\s+|\s*\;|\s*\()
                                    ''', flags=self._ALL_FLAGS)

        re_module_end = re.compile(r'''
                                    \b(?P<end_module>endmodule)
                                    ''', flags=self._ALL_FLAGS)

        for match in re.finditer(re_module_start, code):
            is_tb = re.search(re_tb, code[:match.start()])

            name = match.group('name')
            self.module = self.master.get_verilog_module(name)

            if is_tb:
                self.module.set_is_tb()

            sub_code = code[match.end():]
            end_match = re_module_end.search(sub_code)

            parameter_sub_code = code[match.start():]
            self._parameter(parameter_sub_code, self.module)

            if end_match:
                self._inst_module(sub_code)
                self._testcase(sub_code, self.module)
                self.module.set_complete()

    def _parameter(self, code, module):
        '''
        Locate all module parameters.
        '''
        re_par_start = re.compile(r'''
                                    \bmodule
                                    \s+[a-zA-Z_0-9]+
                                    \s*\#\s*\(
        ''', flags=self._ALL_FLAGS)

        re_par_end = re.compile(r'(\)\s*;)|(\)\s*\()', flags=self._ALL_FLAGS)

        for start_match in re.finditer(re_par_start, code):
            # Find the code section with parameter list
            search_code = code[start_match.end():]
            end_match = re.search(re_par_end, search_code)
            sub_code = search_code[:end_match.start()]

            re_parameter = re.compile(r'''
                                       (\b|\s+)parameter
                                       (\s+[a-zA-Z_0-9]+)?             # paramter type
                                       \s+(?P<name>[a-zA-Z_0-9]+)      # parameter name
                                       \s*=\s*
             ''', flags=self._ALL_FLAGS)

            # Add all paramteres found to the module
            for match in re.finditer(re_parameter, sub_code):
                module.add_parameter(match.group('name'))

    def _inst_module(self, code):
        '''
        Locate all module instantiations inside this module.
        Used for dependency setting.
        '''
        re_inst = re.compile(r'''
        \b
        (?P<inst_name>[a-zA-Z_0-9]+\s+)?
        (?P<name>[a-zA-Z_0-9]+)
        \s+(\#\s*)?\(
        ''', flags=self._ALL_FLAGS)
        matches = re.finditer(re_inst, code)
        for match in matches:
            name = match.group('name')
            self.module.add_int_dep(name)

    def _testcase(self, code, module):
        '''
        Locate all built-in testcases.
        '''
        # Match testcases
        re_tc = re.compile(r'''
                            \s+\(\s*
                            %s
                            \s*==\s*
                            \"(?P<testcase>[a-zA-Z_\-0-9]+)\"\s*
                            \)\s*
        ''' % self.master.testcase_string, flags=self._ALL_FLAGS | re.IGNORECASE)

        matches = re.finditer(re_tc, code)
        for match in matches:
            testcase = str(match.group('testcase'))
            module.add_testcase(testcase)
