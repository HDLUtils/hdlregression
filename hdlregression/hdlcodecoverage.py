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

if __package__ is None or __package__ == '':
    from cmd_runner import CommandRunner
else:
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

        if self.check_code_coverage_legal_chars(settings) is False:
            self.project.logger.warning(
                'Invalid coverge settings in: %s' % (settings))
        else:
            self.code_coverage_settings = settings.replace('-', '')

    def get_code_coverage_settings(self) -> str:
        return self.code_coverage_settings

    def set_code_coverage_file(self, code_coverage_file):
        '''
        Selects the base name of the code coverage report file.
        File name is extracted if set with a path.
        '''
        if not code_coverage_file.lower().endswith('.ucdb'):
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
        legal = [cov_set in self.ID_CODE_COVERAGE for cov_set in code_coverage_settings]
        return all(legal)

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
        match_code_coverage_file = os.path.basename(self.code_coverage_file).lower()

        for root, _, files in os.walk(self.project.settings.get_test_path()):
            for name in files:
                if name.lower() == match_code_coverage_file:
                    merge_file = os.path.join(root, name)
                    merge_file = os.path.abspath(merge_file)
                    merge_file = merge_file.replace('\\', '/')
                    self.file_list.append(merge_file)

        if len(self.file_list) == 0:
            self.project.logger.warning('No code coverage files (UCDB) found.')
            return False
        else:
            return True

    def _insert_to_code_coverage_file_name(self, code_coverage_file_name, text):
        '''
        Inserts a text string to the file name:
            <file_name>.<ext> -->> <file_name><text>.<ucdb>
        and returns the file name.
        '''
        dot_idx = code_coverage_file_name.find('.')
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
        simulator = self.project.settings.get_simulator_name()

        if self.get_code_coverage_file() is not None:
            if simulator == 'GHDL':
                self.project.logger.warning(
                    'Code coverage not supported for GHDL simulator.')
                return False
            else:
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
        else:
            self.__class__ = ModelsimCodeCoverage


class ModelsimCodeCoverage(HdlCodeCoverage):

    ID_CODE_COVERAGE = ['-', 'b', 'c', 'e', 's', 't', 'x', 'f']

    def __init__(self, project):
        super().__init__(project=project)
        self.project = project

    def _merge_code_coverage_files(self) -> str:
        '''
        Executes code coverage merge with all UCDB files found
        in hdlregression/test/ sub-folders.
        '''
        merge_ucdb = self.get_code_coverage_file()
        merge_ucdb = self._insert_to_code_coverage_file_name(merge_ucdb, '_merge')

        merge_command = ['vcover',
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

            exception_command = ['vsim',
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
        report_command = 'vcover report -verbose -code %s -html -output %s %s' % (self.get_code_coverage_settings(),
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
        report_command = 'vcover report -verbose -code %s -output %s %s' % (self.get_code_coverage_settings(),
                                                                            code_coverage_report,
                                                                            ucdb_file)
        self._run_command_str(report_command)


class GHDLCodeCoverage(HdlCodeCoverage):
    
    def __init__(self, project):
        super().__init__(project=project)
        self.project = project