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


import sys

# ----------- USER HDLRegression PATH -----------------
# If HDLRegression is not installed as a Python package (see doc)
# then uncomment the following line and set the path for
# the HDLRegression install folder :
# sys.path.append(<full_or_relative_path_to_hdlregression_install>)

# Import the HDLRegression module to the Python script:
from hdlregression import HDLRegression

# ----------- USER IMPORT -----------------
# Import other Python package(s):

# Define a HDLRegression item to access the HDLRegression functionality:
hr = HDLRegression()

# ------------ USER CONFIG START ---------------

# Add Python functions here if needed:


def add_uvvm_basic(hr):
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/uvvm_util/src/*.vhd",
        library_name="uvvm_util",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/uvvm_vvc_framework/src/*.vhd",
        library_name="uvvm_vvc_framework",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_vip_scoreboard/src/*.vhd",
        library_name="bitvis_vip_scoreboard",
    )


def check_results(hr):
    (passed_tests, failed_tests, not_run_tests) = hr.get_results()

    print("-" * 40)
    print("Test run completed with %d failing tests:" % (len(failed_tests)))
    for test in passed_tests:
        print("Passing: %s" % (test))
    print("-" * 40)
    for test in failed_tests:
        print("Failing: %s" % (test))
    print("-" * 40)
    for test in not_run_tests:
        print("Not run: %s" % (test))


def test_1(hr):
    # ========================================================================
    # Add required UVVM functionality: utility library, framework and Scoreboard
    add_uvvm_basic(hr)

    # ========================================================================
    # Add DUT
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_uart/src/*.vhd",
        library_name="bitvis_uart",
        code_coverage=True,
    )

    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_irqc/src/*.vhd",
        library_name="bitvis_irqc",
    )

    # ========================================================================
    # Add verification IPs
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_vip_sbi/src/*.vhd",
        library_name="bitvis_vip_sbi",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/uvvm_vvc_framework/src_target_dependent/*.vhd",
        library_name="bitvis_vip_sbi",
    )

    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_vip_uart/src/*.vhd",
        library_name="bitvis_vip_uart",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/uvvm_vvc_framework/src_target_dependent/*.vhd",
        library_name="bitvis_vip_uart",
    )

    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_vip_clock_generator/src/*.vhd",
        library_name="bitvis_vip_clock_generator",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/uvvm_vvc_framework/src_target_dependent/*.vhd",
        library_name="bitvis_vip_clock_generator",
    )

    # ========================================================================
    # Add testbench
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_uart/tb/*.vhd",
        library_name="bitvis_uart",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_uart/tb/maintenance_tb/*.vhd",
        library_name="bitvis_uart",
    )

    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_irqc/tb/*.vhd",
        library_name="bitvis_irqc",
    )
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/bitvis_irqc/tb/maintenance_tb/*.vhd",
        library_name="bitvis_irqc",
    )

    # ========================================================================
    # Create test groups
    hr.add_to_testgroup(
        testgroup_name="uart_vvc_tb_all", entity="uart_vvc_tb", architecture="func"
    )
    hr.add_to_testgroup(
        testgroup_name="transmit_tests",
        entity="uart_vvc_tb",
        architecture="func",
        testcase="*transmit*",
    )
    hr.add_to_testgroup(
        testgroup_name="receive_tests",
        entity="uart_vvc_tb",
        architecture="func",
        testcase="*receive*",
    )

    hr.set_simulator_wave_file_format("FST")
    hr.add_to_testgroup(testgroup_name="selection_tests", entity="uart_vvc_demo_tb")
    hr.add_to_testgroup(testgroup_name="selection_tests", entity="uart_simple_bfm_tb")

    # ========================================================================
    # Create testcases to run
    # hr.add_testcase('uart_vvc_tb.func.check_single_simultaneous_transmit_and_receive')
    # hr.add_testcase('uart_vvc_tb.func.check_register_defaults')

    # ========================================================================
    # Setup coverage
    # hr.set_coverage("bcst", "demo_coverage.ucdb")

    # ========================================================================
    # Generate report
    # hr.gen_report(report_file="sim_report.txt", compile_order=True)
    hr.gen_report(report_file="sim_report.json", compile_order=True)

    # ------------ USER CONFIG END ---------------
    # hr.start(sim_options='-t 1ps')
    hr.start()

    # ========================================================================
    # Post-processing results
    check_results(hr)


def test_2(hr):
    hr.add_files(
        filename="../../UVVM/INTERNAL_UVVM/uvvm_util/src/*.vhd",
        library_name="uvvm_util",
    )
    hr.add_files(filename="tb/demo_tb.vhd", library_name="test_2_lib")

    hr.start()


if __name__ == "__main__":
    test_1(hr)
    # test_2(hr)
