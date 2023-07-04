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
    BLUE = '\033[34m'
    WHITE = '\033[37m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    WARNING = '\033[33m'
    FAIL = '\033[31m'
    ENDC = '\033[0m'


class Logger():
    def __init__(self, name, project=None):
        self.name = name
        self.level = 'info'
        self.levels = {'debug': 1, 'info': 2, 'warning': 3, 'error': 4}
        self.project = project

        self.COLORS = {
            'info' : '\033[37m',    # white
            'warning' : '\033[33m', # yellow
            'error' : '\033[31m',   # red
            'debug' : '\033[34m',   # blue
            'green' : '\033[32m',   # green
            'red'   : '\033[31m',   # red
            'endc'  : '\033[0m'     # end color
        }

    def is_gui_mode(self) -> bool:
        if self.project:
            return self.project.settings.get_is_gui_mode()
        else:
            return None

    def use_color(self) -> bool:
        return self.project.settings.get_use_log_color()

    def set_level(self, level):
        self.level = level.lower()

    def set_name(self, name):
        self.name = name

    def colorize(self, msg, color):
        color_code = self.COLORS.get(color, '')
        if color_code:
            return color_code + msg + self.COLORS['endc']
        else:
            return msg

    def log(self, level, msg, end='\n', color=None):
        color = color or level
        if not self.is_gui_mode() and self.use_color():
            msg = self.colorize(msg, color)
        print(msg, end=end)

    def info(self, msg, end='\n', color=None):
        self.log('info', msg, end, color)

    def warning(self, msg, end='\n', color=None):
        self.log('warning', msg, end, color)

    def error(self, msg, end='\n', color=None):
        self.log('error', msg, end, color)

    def debug(self, msg, end='\n', color=None):
        current_level = self.levels.get(self.level)
        if current_level <= self.levels.get('debug'):
            self.log('debug', msg, end, color)

    def red(self):
        return self.COLORS['error'] if self.use_color() is True else ''

    def green(self):
        return self.COLORS['green'] if self.use_color() is True else ''

    def yellow(self):
        return self.COLORS['warning'] if self.use_color() is True else ''

    def reset_color(self):
        return self.COLORS['endc'] if self.use_color() is True else ''
