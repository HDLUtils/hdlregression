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
from abc import abstractmethod

if __package__ is None or __package__ == '':
    from logger import Logger
else:
    from .logger import Logger


class HDLReporter:

    def __init__(self, project=None, filename=None):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        if filename:
            self.set_filename(filename)

        # Setup report items default
        self.set_report_compile_order()
        self.set_report_spec_cov()
        self.set_report_library()
        self.set_report_test_results()
        self.set_report_testcase()
        self.set_report_testgroup()
        self.set_report_files()

    def _check_test_was_run(self) -> bool:
        if self.project.get_num_tests_run() == 0:
            self.logger.debug('No testcases run - skipping reporting.')
            return False
        else:
            return True

    def _is_ci_run(self) -> bool:
        return self.project.settings.get_run_all()

    def _is_testcase_run(self) -> bool:
        return (self.project.settings.get_testcase() is not None)

    def _is_testgroup_run(self) -> bool:
        return (self.project.settings.get_testgroup() is not None)

    def _is_gui_run(self) -> bool:
        return self.project.settings.get_gui_mode()

    def _time_of_run(self) -> str:
        return self.project.settings.get_time_of_run()

    def _time_of_sim(self) -> str:
        return self.project.settings.get_sim_time()

    @classmethod
    def set_report_items(cls, report_compile_order, report_spec_cov, report_library):
        cls.set_report_compile_order(report_compile_order)
        cls.set_report_spec_cov(report_spec_cov)
        cls.set_report_library(report_library)

    @staticmethod
    def get_compile_order(self) -> list:
        self.project._get_compile_order()

    @classmethod
    def set_report_compile_order(cls, enable=True):
        cls.report_compile_order = enable

    @classmethod
    def get_report_compile_order(cls) -> bool:
        return cls.report_compile_order

    @classmethod
    def set_report_spec_cov(cls, enable=False):
        cls.report_spec_cov = enable

    @classmethod
    def get_report_spec_cov(cls) -> bool:
        return cls.report_spec_cov

    @classmethod
    def set_report_library(cls, enable=False):
        cls.report_library = enable

    @classmethod
    def get_report_library(cls) -> bool:
        return cls.report_library

    @classmethod
    def set_report_test_results(cls, enable=True):
        cls.report_test_results = enable

    @classmethod
    def set_report_testcase(cls, enable=True):
        cls.report_testcase = enable

    @classmethod
    def set_report_testgroup(cls, enable=True):
        cls.report_testgroup = enable

    @classmethod
    def set_report_files(cls, enable=False):
        cls.report_files = enable

    def set_filename(self, filename):
        self.filename = filename.lower()

    def get_filename(self) -> str:
        return self.filename

    def get_full_filename(self) -> str:
        return os.path.join(self.project.settings.get_test_path(), self.filename)

    @abstractmethod
    def write_to_file(self):
        pass

    def report(self):
        self.write_to_file()
