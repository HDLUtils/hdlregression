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
import argparse

from .settings import HDLRegressionSettings


def get_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(description="HDLRegression CLI options")


def arg_parser_reader(arg_parser=None):
    # Python 2
    if sys.version_info.major < 3:
        opts_short = [opt.lower() for opt in sys.argv[1:] if opt.startswith("-")]
        opts_long = [opt.lower() for opt in sys.argv[1:] if opt.startswith("--")]
        args = [arg.lower() for arg in sys.argv[1:] if not arg.startswith("-")]
        print("%s, %s, %s" % (opts_short, opts_long, args))
        return None

    # Python 3
    else:
        if arg_parser is None:
            arg_parser = get_parser()

        arg_parser.add_argument(
            "-v", "--verbose", action="store_true", help="enable full verbosity"
        )
        arg_parser.add_argument(
            "-d", "--debug", action="store_true", help="enable debug mode"
        )
        arg_parser.add_argument(
            "-g", "--gui", action="store_true", help="enable simulator GUI mode"
        )
        arg_parser.add_argument(
            "-fr", "--fullRegression", action="store_true", help="run full regression"
        )
        arg_parser.add_argument(
            "-c", "--clean", action="store_true", help="clean before regression run"
        )
        arg_parser.add_argument(
            "-tc",
            "--testCase",
            action="store",
            type=str,
            nargs=1,
            help="run selected testbench[.architecture[.testcase]]",
        )
        arg_parser.add_argument(
            "-tg",
            "--testGroup",
            action="store",
            type=str,
            nargs=1,
            help="run selected testgroup(s)",
        )
        arg_parser.add_argument(
            "-ltc", "--listTestcase", action="store_true", help="list testcases"
        )
        arg_parser.add_argument(
            "-ltg", "--listTestgroup", action="store_true", help="list testgroups"
        )
        arg_parser.add_argument(
            "-lco", "--listCompileOrder", action="store_true", help="list compile order"
        )
        arg_parser.add_argument(
            "-fc", "--forceCompile", action="store_true", help="force recompile"
        )
        arg_parser.add_argument(
            "-sof",
            "--stopOnFailure",
            action="store_true",
            help="stop simulations on testcase fail",
        )
        arg_parser.add_argument(
            "-s",
            "--simulator",
            action="store",
            type=str,
            nargs=1,
            help="select simulator Modelsim/GHDL/NVC/Riviera_Pro/Vivado",
        )
        arg_parser.add_argument(
            "-t",
            "--threading",
            action="store",
            type=int,
            nargs="?",
            const=1,
            help="run tasks in parallel",
        )
        arg_parser.add_argument(
            "-ns",
            "--no_sim",
            action="store_true",
            help="no simulation, only compilation",
        )

        arg_parser.add_argument(
            "--waveFormat",
            action="store",
            type=str,
            nargs=1,
            default="vcd",
            help="wave file format [VCD (default) or FST]",
        )

        arg_parser.add_argument(
            "-ll", "--loggLevel", action="store", type=str, help=argparse.SUPPRESS
        )
        arg_parser.add_argument(
            "-ld", "--listDependency", action="store_true", help=argparse.SUPPRESS
        )
        arg_parser.add_argument(
            "-ca", "--compileAll", action="store_true", help=argparse.SUPPRESS
        )
        arg_parser.add_argument(
            "-cc", "--compileChanges", action="store_true", help=argparse.SUPPRESS
        )

        arg_parser.add_argument(
            "--showWarnError",
            action="store_true",
            help="Show error and warning messages during simulations.",
        )
        arg_parser.add_argument(
            "--noColor", action="store_true", help="Disable terminal output colors."
        )

        args = arg_parser.parse_args(sys.argv[1:])

        return args


def arg_parser_update_settings(settings, args) -> "HDLRegressionSettings":
    settings.set_verbose(args.verbose)
    settings.set_gui_mode(args.gui)
    settings.set_run_all(args.fullRegression)
    settings.set_clean(args.clean)

    if args.listDependency:
        settings.set_list_dependencies(True)

    settings.set_testgroup(args.testGroup)

    if args.loggLevel:
        settings.set_logger_level(args.loggLevel)
    else:
        settings.set_logger_level("info")

    settings.set_list_testcase(args.listTestcase)
    settings.set_list_compile_order(args.listCompileOrder)
    settings.set_list_testgroup(args.listTestgroup)
    settings.set_force_recompile(args.forceCompile)

    if args.threading:
        settings.set_threading(True)
        settings.set_num_threads(args.threading)

    if args.debug:
        settings.set_debug_mode(True)
        settings.set_logger_level("debug")
    else:
        settings.set_debug_mode(False)

    if args.stopOnFailure:
        settings.set_stop_on_failure(True)

    if args.no_sim:
        settings.set_no_sim(True)

    if args.noColor:
        settings.set_use_log_color(False)

    if args.waveFormat:
        settings.set_simulator_wave_file_format(args.waveFormat[0])

    settings.set_gui_compile_changes(args.compileChanges)
    settings.set_gui_compile_all(args.compileAll)

    settings.set_show_err_warn_output(args.showWarnError)

    # ----------------------------------------------
    # Arguments with parameters
    # ----------------------------------------------
    if args.simulator:
        settings.set_simulator_name(simulator_name=args.simulator[0], cli=True)

    settings.set_cli_override(False)

    if args.testGroup:
        settings.set_testgroup(args.testGroup[0])
        settings.set_cli_override(True)

    if args.testCase:
        # Clean the testcase list as we only want to run this/these
        settings.empty_testcase_list()
        settings.set_testcase(args.testCase[0])
        settings.set_cli_override(True)

    return settings
