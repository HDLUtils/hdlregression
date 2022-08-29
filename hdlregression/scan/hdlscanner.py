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

from abc import abstractmethod

if __package__ is None or __package__ == '':
    from container import Container
    from logger import Logger
else:
    from ..struct.container import Container
    from ..report.logger import Logger


class HDLScanner:
    '''
    Base scanner class
    '''

    def __init__(self, project, library, filename, hdlfile):
        self.logger = Logger(name=__name__, project=project)
        self.testcase_string = project.settings.get_testcase_identifier_name()
        self.container = Container()
        self.library = library
        self.filename = filename
        self.hdlfile = hdlfile

        # Lists
        self.library_list = []
        self.int_use_list = []
        self.testcase_list = []

    def get_library(self) -> str:
        return self.library

    def scan(self, file_content):
        file_content = self._clean_code(file_content)
        self.tokenize(file_content)

    def set_filename(self, filename):
        self.filename = filename

    def get_filename(self) -> str:
        return self.filename

    def add_library_dep(self, library):
        if not(library.lower() in self.library_list):
            self.library_list.append(library.lower())

    def get_library_dep(self) -> list:
        '''
        Returns the library list and empties the stored list.
        '''
        library_list_copy = [item for item in self.library_list]
        self.library_list = []
        return library_list_copy

    def add_int_dep(self, use_dep):
        if not(use_dep.lower() in self.int_use_list):
            self.int_use_list.append(use_dep.lower())

    def get_int_dep(self) -> list:
        '''
        Returns the internal use list and empties the stored list.
        '''
        list_copy = [item for item in self.int_use_list]
        self.int_use_list = []
        return list_copy

    def add_testcase(self, testcase):
        if testcase not in self.testcase_list:
            self.testcase_list.append(testcase)

    def get_testcase(self) -> list:
        return self.testcase_list

    def add_module_to_container(self, module):
        module.set_hdlfile(self.hdlfile)
        self.container.add(module)

    def get_module_container(self) -> 'Container':
        return self.container

    @abstractmethod
    def _clean_code(self, file_content_list) -> list:
        pass

    @abstractmethod
    def tokenize(self, file_content_list):
        pass