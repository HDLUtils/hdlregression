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

from .arg_parser import arg_parser_update_settings
from .settings import HDLRegressionSettings
from .report.logger import Logger


class SettingsConfigurator:
    """
    Class for handling project fonfigurations.
    """

    def __init__(self, project=None):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        self.settings = None

    @staticmethod
    def unset_argument_settings(settings) -> "HDLRegressionSettings":
        """
        Restorest any CLI argument adjusted settings back to default.

        args:
            settings (HDLRegressionSettings): the current run settings.
        returns:
            settings (HDLRegressionSettings): the adjusted run settings.
        """
        default_settings = HDLRegressionSettings()
        settings.set_verbose(default_settings.get_verbose())
        settings.set_run_all(default_settings.get_run_all())
        settings.set_debug_mode(default_settings.get_debug_mode())
        settings.set_force_recompile(default_settings.get_force_recompile())
        settings.set_clean(default_settings.get_clean())
        settings.set_testcase(default_settings.get_testcase())
        settings.set_testgroup(default_settings.get_testgroup())
        settings.set_list_testcase(default_settings.get_list_testcase())
        settings.set_list_compile_order(default_settings.get_list_compile_order())
        settings.set_list_testgroup(default_settings.get_list_testgroup())
        settings.set_stop_on_failure(default_settings.get_stop_on_failure())
        settings.set_no_sim(default_settings.get_no_sim())
        return settings

    @staticmethod
    def setup_settings(settings, args) -> "HDLRegressionSettings":
        """
        Adjust the run settings with any selected CLI arguments.
        """
        return arg_parser_update_settings(settings, args)
