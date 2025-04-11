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
import re
from setuptools import setup, find_packages

def get_version(init_file):
    with open(init_file, encoding="utf-8") as f:
        for line in f:
            if line.startswith('__version__'):
                # Note, expecting __version__ = "x.y.z"
                m = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    return m.group(1)
    raise RuntimeError("Kunne ikke finne __version__ i __init__.py")

here = os.path.abspath(os.path.dirname(__file__))
init_file = os.path.join(here, "hdlregression", "__init__.py")
version = get_version(init_file)

def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), encoding="utf-8") as f:
        return f.read()

description = read('./doc/src/description.rst')

setup(name="hdlregression",
      version=version,
      packages=find_packages(),
      include_package_data=True,      
      description=(description),
      license="MIT",
      keywords="regression vhdl verilog",
      url="https://github.com/hdlutils/hdlregression",
      # packages=['hdlregression',
      #           'hdlregression.report',
      #           'hdlregression.run',
      #           'hdlregression.scan',
      #           'hdlregression.construct'],
      long_description=read('README.rst'),
      long_description_content_type="text/x-rst",
     )
