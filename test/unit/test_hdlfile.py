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

from hdlregression.construct.hdlfile import HDLFile
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
    filename = hdlFile.get_filename_with_path()
    exp_name = get_file_path('../tb/my_tb_rand.vhd')
    assert exp_name in filename, 'Expecting init file name'


def test_change_filename():
    exp_filename = get_file_path("../tb/tb_testcase.vhd")
    hdlFile.set_filename(exp_filename)
    get_filename = hdlFile.get_filename_with_path()
    assert get_filename == exp_filename, "Expecting changed file name"


def test_file_type():
    hr = HDLRegression()
    filename = get_file_path("../tb/tb_testcase.vhd")
    hr.add_files(filename, 'filetype_lib')
    hr.start()

    test_lib = hr._get_library_object('filetype_lib')

    assert test_lib.get_name() == "filetype_lib", 'check library located'

    lib_files = test_lib.get_hdlfile_list()
    file_obj = lib_files[0]

    assert file_obj.get_is_vhdl() is True, "check correct file type"


def test_remove():
    hr = HDLRegression()
    filename = get_file_path("../tb/tb_passing*.vhd")
    hr.add_files(filename, 'remove_file_lib')

    hr.remove_file("tb_passing_2.vhd", "remove_file_lib")
    hr.start()

    test_lib = hr._get_library_object('remove_file_lib')
    lib_files = test_lib.get_hdlfile_list()
    lib_files_names = [file.get_filename() for file in lib_files]

    assert len(lib_files_names) == 1, "check number of files"
    assert "tb_passing.vhd" in lib_files_names, "check not deleted file"
    assert "tb_passing_2.vhd" not in lib_files_names, "check deleted file"


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
    hr.start()

    test_lib = hr._get_library_object('filetype_lib')

    assert test_lib.get_name() == "filetype_lib", 'check library located'

    lib_files = test_lib.get_hdlfile_list()
    file_obj = lib_files[0]

    assert file_obj.get_is_netlist() is False, "check VHD file not detected as netlist"


def test_netlist_detection_with_sdf_file():
    hr = HDLRegression()
    filename = get_file_path("../tb/netlist.sdf")
    hr.add_files(filename, 'filetype_lib')
    hr.start()

    test_lib = hr._get_library_object('filetype_lib')

    assert test_lib.get_name() == "filetype_lib", 'check library located'

    lib_files = test_lib.get_hdlfile_list()
    file_obj = lib_files[0]

    assert file_obj.get_is_netlist() is True, "check SDF file detected as netlist"


# ==============================================================
# Netlist SV file
# ==============================================================


def test_add_system_verilog_file_filename_accepted():
    '''
    Test adding SV files.
    '''
    clear_output()
    hr = HDLRegression()

    test_files = get_file_path('../tb/dummy_sv_file.sv')
    hr.add_files(test_files, 'test_lib', parse_file=False)
    hr.start()

    library = hr._get_library_object('test_lib')
    file_list = library.get_hdlfile_list()
    assert file_list[0].get_filename() == 'dummy_sv_file.sv', "check filename"


def test_add_system_verilog_file_filetype():
    '''
    Test adding SV files.
    '''
    from hdlregression.construct.hdlfile import SVFile
    clear_output()
    hr = HDLRegression()

    test_files = get_file_path('../tb/dummy_sv_file.sv')
    hr.add_files(test_files, 'test_lib', parse_file=False)
    hr.start()

    library = hr._get_library_object('test_lib')
    file_list = library.get_hdlfile_list()
    assert isinstance(file_list[0], SVFile) == True, "check filetype object"
