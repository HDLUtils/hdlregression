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

import sys
import os
import shutil
import pytest

from hdlregression.struct.hdlfile import HDLFile
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

    clear_output()
    hdlregression = HDLRegression()
    global hdlFile

    filename = get_file_path('../tb/my_tb_rand.vhd')

    hdlFile = HDLFile(filename_with_path=filename,
                      project=hdlregression,
                      library="my_work_lib",
                      code_coverage=False,
                      hdl_version="2008",
                      parse_file=True,
                      com_options=None)


def tear_down_function():
    if os.path.isdir('./hdlregression'):
        shutil.rmtree('./hdlregression')

# ==============================================================
# File name tests
# ==============================================================


def test_get_filename():
    filename = hdlFile.get_filename()
    exp_name = get_file_path('../tb/my_tb_rand.vhd')
    assert exp_name in filename, 'Expecting init file name'


def test_change_filename():
    exp_filename = get_file_path("../tb/tb_testcase.vhd")
    hdlFile.set_filename(exp_filename)
    get_filename = hdlFile.get_filename()
    assert get_filename == exp_filename, "Expecting changed file name"


def test_file_type():
    hr = HDLRegression()
    filename = get_file_path("../tb/tb_testcase.vhd")
    hr.add_files(filename, 'filetype_lib')

    test_lib = hr._get_library_object('filetype_lib')

    assert test_lib.get_name() == "filetype_lib", 'check library located'

    lib_files = test_lib.get_hdlfile_list()
    file_obj = lib_files[0]

    assert file_obj.get_is_vhdl() is True, "check correct file type"


# ==============================================================
# Library tests
# ==============================================================


def test_get_library():
    library = hdlFile.get_library()
    assert library == "my_work_lib", "Expecting my_work_lib library"


def test_change_library():
    hdlFile.set_library("my_other_lib")
    library = hdlFile.get_library()
    assert library == "my_other_lib", "Expecting changed library"


# ==============================================================
# Netlist tests
# ==============================================================


def test_netlist_detection_with_vhd_file():
    hr = HDLRegression()
    filename = get_file_path("../tb/tb_testcase.vhd")
    hr.add_files(filename, 'filetype_lib')

    test_lib = hr._get_library_object('filetype_lib')

    assert test_lib.get_name() == "filetype_lib", 'check library located'

    lib_files = test_lib.get_hdlfile_list()
    file_obj = lib_files[0]

    assert file_obj.get_is_netlist() is False, "check VHD file not detected as netlist"


def test_netlist_detection_with_sdf_file():
    hr = HDLRegression()
    filename = get_file_path("../tb/netlist.sdf")
    hr.add_files(filename, 'filetype_lib')

    test_lib = hr._get_library_object('filetype_lib')

    assert test_lib.get_name() == "filetype_lib", 'check library located'

    lib_files = test_lib.get_hdlfile_list()
    file_obj = lib_files[0]

    assert file_obj.get_is_netlist() is True, "check SDF file detected as netlist"
