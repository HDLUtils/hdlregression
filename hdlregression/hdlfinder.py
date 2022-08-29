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
from glob import glob

if __package__ is None or __package__ == '':
    from logger import Logger
else:
    from .report.logger import Logger


class HDLFinder:
    '''
    Class for locating files and creating hdlregression file objects.
    '''

    def __init__(self, project, filename=None):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        # Init file name string list as empty list.
        self.file_list = []

        # Locate file(s) based on filename, skip if is dir
        if filename:
            if os.path.isdir(filename):
                self.logger.warning('Filename is directory: %s' % (filename))
            elif filename:
                self.find_files(filename)

    def find_files(self, filename, recursive=False) -> None:
        '''
        Find all files and add to list.
        '''
        if not self.project.settings.get_is_gui_mode():
            filename = os.path.join(
                self.project.settings.get_script_path(), filename)

        filename = os.path.normpath(filename)
        filename = os.path.realpath(filename)

        files = glob(filename, recursive=recursive)

        for item in files:
            if not(item in self.file_list):
                self.file_list.append(item)

    def get_file_list(self) -> list:
        '''
        Return list of all files found.
        '''
        return self.file_list
