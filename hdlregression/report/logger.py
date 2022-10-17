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


class bcolors:
    HEADER = '\033[35m'
    OKBLUE = '\033[34m'
    OKGREEN = '\033[32m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'


class Logger():
    '''

    '''

    def __init__(self, name, project=None):
        self.name = name
        self.level = 'info'
        self.color = 'white'
        self.levels = {'debug': 1, 'info': 2, 'warning': 3, 'error': 4}
        self.project = project

    def is_gui_mode(self) -> bool:
        if self.project:
            return self.project.settings.get_is_gui_mode()
        else:
            return None

    def info(self, msg, color='white', end='\n'):
        if self.is_gui_mode():
            print(msg, end=end)
        elif color.lower() == 'green':
            print(bcolors.OKGREEN + msg + bcolors.ENDC, end=end)
        elif color.lower() == 'blue':
            print(bcolors.OKBLUE + msg + bcolors.ENDC, end=end)
        elif color.lower() == 'header':
            print(bcolors.HEADER + msg + bcolors.ENDC, end=end)
        else:
            print(msg, end=end)

    def warning(self, msg, end='\n'):
        if self.is_gui_mode():
            print(msg, end=end)
        else:
            print(bcolors.WARNING + msg + bcolors.ENDC, end=end)

    def error(self, msg, end='\n'):
        if self.is_gui_mode():
            print(msg, end=end)
        else:
            print(bcolors.FAIL + msg + bcolors.ENDC, end=end)

    def debug(self, msg, end='\n'):
        current_level = self.levels.get(self.level)
        if current_level <= self.levels.get('debug'):
            if self.is_gui_mode():
                print(msg, end=end)
            else:
                print(bcolors.HEADER + '[' + self.name + ':debug] ' + msg + bcolors.ENDC, end=end)

    def set_level(self, level):
        self.level = level.lower()

    def set_name(self, name):
        self.name = name

    def green(self):
        return bcolors.OKGREEN

    def red(self):
        return bcolors.FAIL

    def yellow(self):
        return bcolors.WARNING

    def reset_color(self):
        return bcolors.ENDC

    def str_info(self, msg, color='white', end='\n') -> str:
        if self.is_gui_mode():
            return str(msg, end=end)
        elif color.lower() == 'green':
            return str(bcolors.OKGREEN + msg + bcolors.ENDC, end=end)
        elif color.lower() == 'blue':
            return str(bcolors.OKBLUE + msg + bcolors.ENDC, end=end)
        elif color.lower() == 'header':
            return str(bcolors.HEADER + msg + bcolors.ENDC, end=end)
        else:
            return str(msg, end=end)

    def str_warning(self, msg, end='\n') -> str:
        if self.is_gui_mode():
            return str(msg, end=end)
        else:
            return str(bcolors.WARNING + msg + bcolors.ENDC, end=end)

    def str_error(self, msg, end='\n') -> str:
        if self.is_gui_mode():
            return str(msg, end=end)
        else:
            return str(bcolors.FAIL + msg + bcolors.ENDC, end=end)

    def str_debug(self, msg, end='\n') -> str:
        current_level = self.levels.get(self.level)
        if current_level <= self.levels.get('debug'):
            if self.is_gui_mode():
                return str(msg, end=end)
            else:
                return str(bcolors.HEADER + '[' + self.name + ':debug] ' + msg + bcolors.ENDC, end=end)