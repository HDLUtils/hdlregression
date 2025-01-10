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
import fnmatch
from pathlib import Path
from .report.logger import Logger


class HDLFinder:
    """
    Class for locating files and creating hdlregression file objects.
    """

    def __init__(self, project, filename=None):
        self.logger = Logger(name=__name__, project=project)
        self.project = project
        self.file_list = []  # Init file name string list as empty list.

        if filename:
            if os.path.isdir(filename):
                self.logger.warning("Filename is directory: %s" % filename)
            else:
                self.find_files(filename)

    def find_files(self, filename, recursive=False) -> None:
        """
        Find all files matching 'filename' (case-insensitive).
        Adds matched file paths to self.file_list if not already present.
        """
        script_path = (
            self.project.settings.get_script_path()
            if not self.project.settings.get_is_gui_mode()
            else ""
        )
        search_path = os.path.join(script_path, filename)
        search_path = os.path.normpath(search_path)
        search_dir = os.path.dirname(search_path) or "."
        search_pattern = os.path.basename(search_path)
    
        # Check if the directory exists
        if not Path(search_dir).is_dir():
            return
    
        def gather_candidate_paths(directory: str, recurse: bool):
            """
            Gathers potential (root, filename) pairs either from a single directory 
            or by walking the directory tree, depending on 'recurse'.
            """
            items = []
            if recurse:
                for root, _, files in os.walk(directory):
                    for f in files:
                        items.append((root, f))
            else:
                for f in os.listdir(directory):
                    items.append((directory, f))
            return items
    
        candidates = gather_candidate_paths(search_dir, recursive)
    
        for root, name in candidates:
            if fnmatch.fnmatch(name.lower(), search_pattern.lower()):
                full_path = os.path.join(root, name)
                if full_path not in self.file_list:
                    self.file_list.append(full_path)

    def get_file_list(self) -> list:
        """
        Return list of all files found.
        """
        return self.file_list
