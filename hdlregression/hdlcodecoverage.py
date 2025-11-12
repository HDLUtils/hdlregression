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

from .run.cmd_runner import CommandRunner


class HdlCodeCoverage:

    ID_CODE_COVERAGE = []

    def __init__(self, project):
        self.project = project
        self.file_list = []
        self.code_coverage_file = None
        self.test_path = None
        self.exclude_file = None
        self.code_coverage_settings = None
        self.options = None

    def set_options(self, options):
        if options is not None:
            if not isinstance(options, str):
                self.project.logger.error(
                    'Code coverage options not correct type: type<str>.')
                return
            self.options = options

    def get_options(self) -> str:
        return self.options

    def _create_path_if_missing(self, path):
        if os.path.exists(path) is False:
            os.mkdir(path)

    def get_code_coverage_path(self):
        '''
        Returns the absolute path of hdlregression/test/coverage folder.
        '''
        code_coverage_path = os.path.join(
            self.project.settings.get_test_path(), 'coverage')
        code_coverage_path = os.path.abspath(code_coverage_path)
        self._create_path_if_missing(code_coverage_path)
        return code_coverage_path

    def set_code_coverage_settings(self, settings):
        if not isinstance(settings, str):
            self.project.logger.error('Code coverage settings not correct type: type<str>.')
            return
        self.code_coverage_settings = settings.replace('-', '')

    def get_code_coverage_settings(self) -> str:
        return self.code_coverage_settings

    def set_code_coverage_file(self, code_coverage_file):
        '''
        Selects the base name of the code coverage report file.
        File name is extracted if set with a path.
        '''
        if not code_coverage_file.lower().endswith('.ucdb') and \
           not code_coverage_file.lower().endswith(".acdb"):
            self.project.logger.warning(
                'Code coverage file %s is not a .ucdb file.' % (code_coverage_file))
            code_coverage_file += '.ucdb'

        # Only want the filename (if user provided with a path)
        (_, code_coverage_file_name) = os.path.split(
            os.path.abspath(code_coverage_file))
        # Adjust filename to point to the test/coverage output folder
        code_coverage_file = os.path.join(
            self.get_code_coverage_path(), code_coverage_file_name)
        self.code_coverage_file = code_coverage_file.replace('\\', '/')

    def get_code_coverage_file(self) -> str:
        return self.code_coverage_file

    def set_exclude_file(self, exclude_file):
        if exclude_file is not None:
            script_path = self.project.settings.get_script_path()
            self.exclude_file = os.path.join(script_path, exclude_file)
            self.exclude_file = self.exclude_file.replace('\\', '/')

    def get_exclude_file(self) -> str:
        return self.exclude_file

    def check_code_coverage_legal_chars(self, code_coverage_settings) -> bool:
        '''
        Validates code coverage settings characters.
        '''
        if code_coverage_settings:
            legal = [cov_set in self.ID_CODE_COVERAGE for cov_set in code_coverage_settings]
            return all(legal)
        else:
            return True

    def get_simulator_exec(self, command) -> str:
      return self.project.settings.get_simulator_exec(command)

    def _run_command_str(self, command):
        verbose = self.project.settings.get_verbose()
        self.project.logger.debug('HDLCodeCoverage executing: %s' % (command))
        self.project.run_command(command, verbose=verbose)

    def _run_command_list(self, command, path='./', output_file=None):
        verbose = self.project.settings.get_verbose()
        self.project.logger.debug('HDLCodeCoverage executing: %s' % (command))
        cmd_runner = CommandRunner(project=self.project)
        for line, success in cmd_runner.run(command=command,
                                            path=path,
                                            env=os.environ.copy(),
                                            output_file=output_file):
            if verbose is True:
                print(line.strip())

    def _find_code_coverage_files(self) -> bool:
        '''
        Searches for code coverage files in hdlregression/test folder,
        Note! code coverage files are matched with user file name from set_code_coverage() method.
        '''
        return True

    def _insert_to_code_coverage_file_name(self, code_coverage_file_name, text):
        '''
        Inserts a text string to the file name:
            <file_name>.<ext> -->> <file_name><text>.<ucdb>
        and returns the file name.
        '''
        dot_idx = code_coverage_file_name.rfind('.')
        code_coverage_file_name = code_coverage_file_name[:dot_idx] + \
            text + code_coverage_file_name[dot_idx:]
        return code_coverage_file_name

    def _merge_code_coverage_files(self) -> str:
        '''
        Executes code coverage merge with all UCDB files found
        in hdlregression/test/ sub-folders.
        '''
        return ''

    def _apply_exceptions(self) -> str:
        '''
        Executes code coverage exceptions (TCL file) if set and
        returns the correct UCDB file to generate reports from.
        '''
        return ''

    def _create_code_coverage_sub_folder(self, path_name) -> str:
        '''
        Creates a folder inside the test/coverage folder and
        returns the folder path.
        '''
        path = os.path.join(self.get_code_coverage_path(), path_name)
        path = os.path.abspath(path)
        path = path.replace('\\', '/')
        self._create_path_if_missing(path)
        return path

    def _generate_html_report(self, ucdb_file):
        '''
        Executes code coverage command for HTML report.
        '''
        pass

    def _generate_txt_report(self, ucdb_file):
        '''
        Executes code coverage command for TXT report.
        '''
        pass

    def merge_code_coverage(self) -> bool:
        '''
        Search for code coverage files in hdlregression/test sub-folders and
        save a merge in hdlregression/test/coverage.
        '''
        return True

    def get_code_coverage_obj(self, simulator=None):
        '''
        Changes the HDLCodeCoverage instance to a sub-class object.
        '''
        if simulator is None:
            self.__class__ = ModelsimCodeCoverage
        elif simulator == 'MODELSIM':
            self.__class__ = ModelsimCodeCoverage
        elif simulator == 'GHDL':
            self.__class__ = GHDLCodeCoverage
        elif simulator == 'RIVIERA-PRO':
            self.__class__ = RivieraProCodeCoverage            
        else:
            self.__class__ = ModelsimCodeCoverage


class ModelsimCodeCoverage(HdlCodeCoverage):

    ID_CODE_COVERAGE = ['-', 'b', 'c', 'e', 's', 't', 'x', 'f']

    def __init__(self, project):
        super().__init__(project=project)
        self.project = project

    def merge_code_coverage(self) -> bool:
        '''
        Search for code coverage files in hdlregression/test sub-folders and
        save a merge in hdlregression/test/coverage.
        '''
        # Validate coverage settings
        if self.check_code_coverage_legal_chars(self.code_coverage_settings) is False:
            self.project.logger.warning('Invalid coverage settings in: %s' % (self.code_coverage_settings))
            return False

        if self.get_code_coverage_file() is not None:
            self.project.logger.info('Creating code coverage reports...')
            code_coverage_files_found = self._find_code_coverage_files()

            if code_coverage_files_found:
                # Create test/coverage output folder
                code_coverage_path = os.path.join(
                    self.project.settings.get_test_path(), 'coverage')
                code_coverage_path = os.path.abspath(code_coverage_path)
                self._create_path_if_missing(code_coverage_path)

                # Merge coverage files to one combined coverage file.
                self._merge_code_coverage_files()

                # Apply coverage exceptions.
                ucdb_file = self._apply_exceptions()

                # Write coverage reports.
                self._generate_html_report(ucdb_file)
                self._generate_txt_report(ucdb_file)
                return True
            else:
                return False

        # Coverage not enabled
        else:
            # Don't trigger warning in HDLRegression
            return True

    def _find_code_coverage_files(self) -> bool:
        '''
        Searches for code coverage files in hdlregression/test folder,
        Note! code coverage files are matched with user file name from set_code_coverage() method.
        '''
        match_code_coverage_file = os.path.basename(self.code_coverage_file).lower()

        for root, _, files in os.walk(self.project.settings.get_test_path()):
            for name in files:
                if name.lower() == match_code_coverage_file:
                    merge_file = os.path.join(root, name)
                    merge_file = os.path.abspath(merge_file)
                    merge_file = merge_file.replace('\\', '/')
                    self.file_list.append(merge_file)

        if len(self.file_list) == 0:
            self.project.logger.warning('No code coverage files found.')
            return False
        else:
            return True

    def _merge_code_coverage_files(self) -> str:
        '''
        Executes code coverage merge with all UCDB files found
        in hdlregression/test/ sub-folders.
        '''
        merge_ucdb = self.get_code_coverage_file()
        merge_ucdb = self._insert_to_code_coverage_file_name(merge_ucdb, '_merge')

        vcover_exec = self.get_simulator_exec('vcover')
        merge_command = [vcover_exec,
                         'merge']

        if self.get_options() is not None:
            merge_options = list(self.get_options().split(' '))
            for option in merge_options:
                merge_command.append(option)

        for item in self.file_list:
            merge_command.append(item)

        merge_command.append('-out')
        merge_command.append(merge_ucdb)
        self._run_command_list(merge_command)
        return merge_ucdb

    def _apply_exceptions(self) -> str:
        '''
        Executes code coverage exceptions (TCL file) if set and
        returns the correct UCDB file to generate reports from.
        '''
        exclude_file = self.get_exclude_file()
        code_coverage_ucdb = self.get_code_coverage_file()
        merge_ucdb = self._insert_to_code_coverage_file_name(
            code_coverage_ucdb, '_merge')

        if exclude_file is not None:
            filtered_ucdb = self._insert_to_code_coverage_file_name(
                code_coverage_ucdb, '_filter')
            
            vsim_exec = self.get_simulator_exec('vsim')

            exception_command = [vsim_exec,
                                 '-c',
                                 '-viewcov',
                                 merge_ucdb,
                                 '-do',
                                 'do %s' % (exclude_file),
                                 '-do',
                                 'coverage save %s;exit' % (filtered_ucdb)]
            self._run_command_list(exception_command)
            return filtered_ucdb
        else:
            return merge_ucdb

    def _generate_html_report(self, ucdb_file):
        '''
        Executes code coverage command for HTML report.
        '''
        html_path = os.path.join(self.get_code_coverage_path(), 'html')
        html_path = os.path.abspath(html_path)
        html_path = html_path.replace('\\', '/')
        vcover_exec = self.get_simulator_exec('vcover')
        report_command = '%s report -verbose -code %s -html -output %s %s' % (vcover_exec,
                                                                              self.get_code_coverage_settings(),
                                                                              html_path,
                                                                              ucdb_file)
        self._run_command_str(report_command)

    def _generate_txt_report(self, ucdb_file):
        '''
        Executes code coverage command for TXT report.
        '''
        txt_path = self._create_code_coverage_sub_folder('txt')

        code_coverage_report = os.path.join(txt_path, 'coverage.txt')
        code_coverage_report = os.path.abspath(code_coverage_report)
        code_coverage_report = code_coverage_report.replace('\\', '/')
        vcover_exec = self.get_simulator_exec('vcover')
        report_command = '%s report -verbose -code %s -output %s %s' % (vcover_exec,
                                                                        self.get_code_coverage_settings(),
                                                                        code_coverage_report,
                                                                        ucdb_file)
        self._run_command_str(report_command)


class GHDLCodeCoverage(HdlCodeCoverage):
    
    def __init__(self, project):
        super().__init__(project=project)
        self.project = project



class RivieraProCodeCoverage(HdlCodeCoverage):
    ID_CODE_COVERAGE = ['b', 'c', 'e', 's', 't', 'x', 'f']

    def __init__(self, project):
        super().__init__(project=project)
        self.project = project

    def _find_code_coverage_files(self) -> bool:
        """
        Finds all .acdb files in the test tree for merging.
        """
        self.file_list = []
        for root, _, files in os.walk(self.project.settings.get_test_path()):
            for name in files:
                if name.lower().endswith('.acdb'):
                    acdb_file = os.path.join(root, name)
                    acdb_file = os.path.abspath(acdb_file).replace('\\', '/')
                    self.file_list.append(acdb_file)
        return len(self.file_list) > 0

    def _merge_code_coverage_files(self) -> str:
        if len(self.file_list) <= 1:
            if len(self.file_list) == 1:
                return self.file_list[0]
            else:
                return None
        merged_acdb = self._insert_to_code_coverage_file_name(self.get_code_coverage_file(), '_merge')
        file_list_str = ' '.join(['-i "{}"'.format(f) for f in self.file_list])
        tcl_cmd = 'coverage merge -o "{}" {}; quit;'.format(merged_acdb, file_list_str)
        vsim_exec = self.get_simulator_exec('vsimsa')
        command = [vsim_exec, '-c', '-do', tcl_cmd]
        self._run_command_list(command)
        return merged_acdb

    def merge_code_coverage(self) -> bool:
        if self.get_code_coverage_file() is not None:
            self.project.logger.info('Creating Riviera-PRO code coverage reports...')
            files_found = self._find_code_coverage_files()
            if not files_found:
                self.project.logger.warning('No code coverage files (.acdb) found.')
                return False
            merged_acdb = self._merge_code_coverage_files()
            if not merged_acdb:
                return False
            self._generate_html_report(merged_acdb)
            self._generate_txt_report(merged_acdb)
            return True
        return True

    def _generate_html_report(self, acdb_file):
        html_path = os.path.join(self.get_code_coverage_path(), 'html')
        html_path = os.path.abspath(html_path)
        os.makedirs(html_path, exist_ok=True)
        html_file = os.path.join(html_path, "coverage_report.html")
        tcl_cmd = (
            'coverage open "{}"; '
            'coverage report -html -o "{}"; '
            'quit;'
        ).format(acdb_file, html_file)
        vsim_exec = self.get_simulator_exec('vsimsa')
        command = [vsim_exec, '-c', '-do', tcl_cmd]
        self._run_command_list(command)

    def _generate_txt_report(self, acdb_file):
        """
        Generates a code coverage text report using Riviera-PRO.
        The report is saved in the test/coverage/txt/ directory.
        """
        # Lag output-mappen hvis den ikke finnes
        txt_path = self._create_code_coverage_sub_folder('txt')
        txt_file = os.path.join(txt_path, "coverage.txt")
        txt_file = os.path.abspath(txt_file).replace('\\', '/')

        # Bygg TCL-kommandoen som åpner .acdb og skriver summary til fil
        tcl_cmd = (
            'coverage open "{}"; '
            'coverage report -summary > "{}"; '
            'quit;'
        ).format(acdb_file, txt_file)

        # Finn simulatorens batch-exe
        vsim_exec = self.get_simulator_exec('vsimsa')

        # Kjør batch-kommandoen
        command = [vsim_exec, '-c', '-do', tcl_cmd]
        self._run_command_list(command)