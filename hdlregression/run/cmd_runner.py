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

import subprocess
import os
import sys
from threading import Thread
from queue import Queue, Empty

from ..report.logger import Logger


class HDLRunnerError(Exception):
    pass


class TestOutputPathError(HDLRunnerError):

    def __init__(self, path):
        self.path = path

    def __str__(self):
        return f"Error when trying to create test output path {self.path}."


class CommandExecuteError(HDLRunnerError):

    def __init__(self, command):
        self.command = command
        self.logger = Logger(name=__name__)

    def __str__(self):
        return self.logger.str_error(f"Error executing: {self.command}.")


class CommandRunner:
    '''
    Runs OS commands using subprocesses.
    '''

    ON_POSIX = 'posix' in sys.builtin_module_names

    def __init__(self, project):
        self.logger = Logger(name=__name__, project=project)
        self.project = project

    @staticmethod
    def _enqueue_output(out_fd, queue, transcript_file_path, error):
        '''Reads from the 'out' file descriptor and puts it in a queue and optionally a transcript file.
           Used for os-independent non-blocking reads.
        '''
        try:
            if transcript_file_path:
                with open(transcript_file_path, 'a') as transcript_file:
                    for line in iter(out_fd.readline, ""):
                        queue.put((line, not error))
                        transcript_file.write(line)
            else:
                for line in iter(out_fd.readline, ""):
                    queue.put((line, not error))
        except ValueError:  # We get a value error if 'out_fd' is closed by the subprocess
            pass
        out_fd.close()

    def _get_process(self, command, path):
        return subprocess.Popen(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                universal_newlines=True,  # Stdout/stderr are opened in text mode
                                cwd=path,
                                close_fds=self.ON_POSIX)  # Close filehandles when done (Only Linux)


    def run(self, command, path='./', env=None, output_file=None, timeout=None) -> tuple:
        command = self._convert_to_list(command)

        self._create_path_if_missing(path)

        return_code = None
        popen = None

        ignored_simulator_exit_codes = self.project.settings.get_ignored_simulator_exit_codes()

        try:
            popen = self._get_process(command, path)
            q_transcript = Queue()
            t_stdout = Thread(target=self._enqueue_output, args=(
                popen.stdout, q_transcript, output_file, False))
            t_stderr = Thread(target=self._enqueue_output, args=(
                popen.stderr, q_transcript, output_file, True))
              
            t_stdout.daemon = True  # thread dies with the program
            t_stderr.daemon = True  # thread dies with the program
            t_stdout.start()
            t_stderr.start()
            while True:
                try:
                    transcript_line = q_transcript.get_nowait()
                    yield transcript_line
                except Empty:
                    transcript_line = None

                if return_code is not None:
                    # Program exited and there is no more data in queues
                    break
                if transcript_line is None:
                    return_code = popen.poll()
                    if return_code is not None:
                        # Subprocess finished, wait for the threads to complete
                        t_stdout.join()
                        t_stderr.join()

        except FileNotFoundError as e:
            self.logger.error('Command error: %s.' % (e))
        except OSError as e:
            self.logger.error('Command error: %s.' % (e))
        except subprocess.TimeoutExpired:
            self.logger.error('Test timeout')
        except:
            tb = sys.exc_info()[2]
            raise CommandExecuteError(command).with_traceback(tb)
        if return_code is None and popen is not None:
            return_code = popen.returncode
        if return_code != 0:
            if return_code not in ignored_simulator_exit_codes:
                yield f"Error: Program ended with exit code {format(return_code)}", False
        return

    def _convert_to_list(self, command) -> list:
        # Convert command to list
        if isinstance(command, tuple):
            command = ' '.join(command)
        elif isinstance(command, str):
            command = [command]
        return command

    def _create_path_if_missing(self, path) -> None:
        try:
            if not(os.path.exists(path)):
                os.mkdir(path)
                self.logger.debug("Creating path: %s" % (path))
        except Exception as e:
            TestOutputPathError(path)

    def _get_env(self, env):
        if not env:
            env = os.environ.copy()
        return env

    def gui_run(self, command, path='./', env=None, output_file=None) -> tuple:
        '''
        Execute GUI
        '''
        env = self._get_env(env)

        self._create_path_if_missing(path)

        command = self._convert_to_list(command)

        with subprocess.Popen(command,
                              env=env,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT,
                              bufsize=-1,
                              universal_newlines=True,
                              cwd=path) as sp:
            line, errors = sp.communicate()
            return_code = sp.returncode

            if output_file:
                with open(output_file, 'a') as transcript_file:
                    transcript_file.write(line)

        return line, errors, return_code

    def script_run(self, command, path=None, verbose=False) -> tuple:
        '''
        Used when execute terminal command using HDLRegression API.
        '''
        return_txt = ''

        if path is None:
            path = './'

        command = self._convert_to_list(command)

        popen = subprocess.Popen(command,
                                 stdout=subprocess.PIPE,
                                 universal_newlines=True,
                                 cwd=path)

        for stdout_line in iter(popen.stdout.readline, ""):
            if verbose is True:
                print(stdout_line.rstrip())

            return_txt += stdout_line

        popen.stdout.close()
        return_code = popen.wait()

        return (return_txt, return_code)
