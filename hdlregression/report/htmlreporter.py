#
# Copyright (c) 2025 by HDLRegression Authors. All rights reserved.
# Licensed under the MIT License.
#

from .hdlreporter import HDLReporter


class HTMLReporter(HDLReporter):
    '''
    HDLReporter sub-class for generating HTML reports of regression results.
    '''

    def __init__(self, project=None, filename=None):
        super().__init__(project=project, filename=filename or 'hdlregression_report.html')

    def _html_header(self) -> str:
        return '''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>HDLRegression Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #003366; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; }
        th { background-color: #f2f2f2; }
        .pass { color: green; }
        .fail { color: red; }
        .notrun { color: gray; }
    </style>
</head>
<body>
<h1>HDLRegression Report</h1>
'''

    def _html_footer(self) -> str:
        return '</body>\n</html>'

    def write_to_file(self) -> None:
        if not self._check_test_was_run():
            return

        with open(self.get_full_filename(), 'w') as f:
            f.write(self._html_header())

            # Run Settings
            f.write('<h2>Run Settings</h2>\n<ul>\n')
            f.write(f'<li>CI Run: {self._is_ci_run()}</li>\n')
            f.write(f'<li>Testcase Run: {self._is_testcase_run()}</li>\n')
            f.write(f'<li>Testgroup Run: {self._is_testgroup_run()}</li>\n')
            f.write(f'<li>GUI Mode: {self._is_gui_run()}</li>\n')
            f.write(f'<li>Time of Run: {self._time_of_run()}</li>\n')
            f.write(f'<li>Time of Sim: {self._time_of_sim()} ms</li>\n')
            f.write('</ul>\n')

            # Test Results
            pass_tests, fail_tests, not_run_tests = self.project.get_results()
            f.write('<h2>Test Results</h2>\n')

            def write_test_list(title, tests, css_class):
                f.write(f'<h3>{title} ({len(tests)})</h3>\n<ul>\n')
                for t in tests:
                    f.write(f'<li class="{css_class}">{t}</li>\n')
                f.write('</ul>\n')

            write_test_list("Passing Tests", pass_tests, "pass")
            write_test_list("Failing Tests", fail_tests, "fail")
            write_test_list("Not Run Tests", not_run_tests, "notrun")

            # Testcases
            f.write('<h2>Testcases</h2>\n<ul>\n')
            for library in self.project.library_container.get():
                for hdlfile in library.get_hdlfile_list():
                    for tb_module in hdlfile.get_tb_modules():
                        for arch_module in tb_module.get_architecture():
                            f.write('<li>%s.%s<ul>\n' % (tb_module.get_name(), arch_module.get_name()))
                            for testcase in arch_module.get_testcase():
                                f.write('<li>%s</li>\n' % testcase)
                            f.write('</ul></li>\n')
            f.write('</ul>\n')

            # Testgroups
            f.write('<h2>Testgroups</h2>\n<ul>\n')
            for testgroup_container in self.project.testgroup_collection_container.get():
                f.write(f'<li>{testgroup_container.get_name()}<ul>\n')
                for idx, item in enumerate(testgroup_container.get()):
                    entity, arch, testcase, generics = item
                    line = f'{idx+1}: {entity}'
                    if arch:
                        line += f'.{arch}'
                    if testcase:
                        line += f'.{testcase}'
                    if generics:
                        line += f', generics={generics}'
                    f.write(f'<li>{line}</li>\n')
                f.write('</ul></li>\n')
            f.write('</ul>\n')

            # Compile Order
            if self.get_report_compile_order():
                f.write('<h2>Compilation Order</h2>\n<ul>\n')
                for library in self.project.library_container.get():
                    f.write(f'<li>{library.get_name()}<ul>\n')
                    for idx, module in enumerate(library.get_compile_order_list()):
                        tb = " (TB)" if module.get_is_tb() else ""
                        f.write(f'<li>File {idx+1}: {module.get_filename()}{tb}</li>\n')
                    f.write('</ul></li>\n')
                f.write('</ul>\n')

            # Library Info
            if self.get_report_library():
                f.write('<h2>Library Information</h2>\n<ul>\n')
                for library in self.project.library_container.get():
                    f.write(f'<li>{library.get_name()}<ul>\n')
                    for mod in library._get_list_of_lib_modules():
                        f.write(f'<li>{mod.get_type()}: {mod.get_name()}</li>\n')
                    f.write('</ul></li>\n')
                f.write('</ul>\n')

            f.write(self._html_footer())