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


class HDLContainerError(Exception):
    pass


class ContainerIndexError(HDLContainerError):
    def __init__(self, index):
        self.index = index

    def __str__(self):
        return 'Error when accessing container index: %d.' % (self.index)


class ContainerNameError(HDLContainerError):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Error when accessing container name: %s.' % (self.name)


class ContainerIndexTypeError(HDLContainerError):
    def __init__(self, type_name):
        self.type_name = type_name

    def __str__(self):
        return 'Error when accessing container index of type: %s.' % (self.type_name)


class Container:
    def __init__(self, name=None):
        self.storage = []
        self.name = name.lower() if name else "no_name"

    def add(self, element) -> bool:
        if element not in self.storage:
            self.storage.append(element)
            return True
        else:
            return False

    def add_element_from_list(self, element_list):
        if isinstance(element_list, list):
            for element in element_list:
                self.add(element)

    def get_index(self, index=0):
        if isinstance(index, int) is False:
            raise ContainerIndexTypeError(index)
        try:
            return self.storage[index]
        except:
            raise ContainerIndexError(index)

    def get(self, name=None) -> list:
        if not name:
            return self.storage
        else:
            for element in self.storage:
                try:
                    if element.get_name().lower() == name.lower():
                        return element
                except:
                    raise ContainerNameError(name)
        return Container()

    def remove(self, element_name) -> None:
        if isinstance(element_name, str):
            temp_list = [element for element in self.storage
                         if element.get_name().lower() != element_name.lower()]
        else:
            temp_list = [element for element in self.storage
                         if element.get_name().lower() != element_name.get_name().lower()]
        self.storage = temp_list

    def num_elements(self) -> int:
        return len(self.storage)

    def set_name(self, name):
        self.name = name.lower()

    def get_name(self) -> str:
        return self.name

    def empty_list(self) -> int:
        self.storage = []

    def exists(self, name) -> bool:
        for element in self.storage:
            if element.get_name().lower() == name.lower():
                return True
        return False

    def update(self, item) -> bool:
        for element in self.storage:
            try:
                if element.get_name() == item.get_name():
                    element = item
                    return True
            except:
                raise ContainerNameError(item.get_name())
        return False
