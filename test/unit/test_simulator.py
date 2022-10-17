# ================================================================================================================================
#  Copyright 2021 Bitvis
#  Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0 and in the provided LICENSE.TXT.
#
#  Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
#  an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and limitations under the License.
# ================================================================================================================================
#  Note : Any functionality not explicitly described in the documentation is subject to change at any time
# --------------------------------------------------------------------------------------------------------------------------------

import pytest
import sys
import os
import shutil
import fnmatch


from hdlregression import HDLRegression


if len(sys.argv) >= 2:
    '''
    Remove pytest from argument list
    '''
    sys.argv.pop(1)


def get_file_path(path) -> str:
    '''
    Adjust file paths to match running directory.
    '''
    TEST_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(TEST_DIR, path)


def clear_output():
    if os.path.isdir('./hdlregression'):
        shutil.rmtree('./hdlregression')


def setup_function():
    if os.path.isdir('./hdlregression'):
        print('WARNING! hdlregression folder already exist!')


def tear_down_function():
    if os.path.isdir('./hdlregression'):
        shutil.rmtree('./hdlregression')


def test_set_simulator():
    clear_output()
    hr = HDLRegression()
    simulator = hr.settings.get_simulator_name()
    assert simulator == 'MODELSIM', "Checking default simulator"


def test_set_ghdl_simulator():
    clear_output()
    hr = HDLRegression(simulator="GHDL")
    simulator = hr.settings.get_simulator_name()
    assert simulator == 'GHDL', "Checking updated simulator"

def test_set_ghdl_sim_options_list(capsys):
    clear_output()
    hr = HDLRegression(simulator="GHDL")

    filename = '../tb/tb_passing.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'test_lib')
    hr.set_result_check_string('passing testcase')

    result = hr.start(sim_options=['--wave=wave_file.tst', '--vcd=vcd_file.tst'])

    matches = []
    for root, dirnames, filenames in os.walk('./hdlregression/test/'):
        for filename in fnmatch.filter(filenames, '*_file.tst'):
            matches.append(os.path.join(root, filename))

    assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."


def test_set_ghdl_sim_options_string(capsys):
    clear_output()
    hr = HDLRegression(simulator="GHDL")

    filename = '../tb/tb_passing.vhd'
    filename = get_file_path(filename)
    hr.add_files(filename, 'test_lib')
    hr.set_result_check_string('passing testcase')

    result = hr.start(sim_options='--wave=wave_file.tst --vcd=vcd_file.tst')

    matches = []
    for root, dirnames, filenames in os.walk('./hdlregression/test/'):
        for filename in fnmatch.filter(filenames, '*_file.tst'):
            matches.append(os.path.join(root, filename))

    assert len(matches) == 2, "checking sim_options for wave/vcd_file.tst exists."

