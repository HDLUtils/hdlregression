.. role:: bash(code)
   :language: bash

#######################################################################################################################
Application Programming Interface (API)
#######################################################################################################################

HDLRegression is configured and run using a Python script that imports the HDLRegression module and 
uses a set of API methods. Because HDLRegression is written in Python the test designer can 
utilize the full Python API and modules to make advanced regression scripts.
There are two template script files in the :bash:`/template` folder to help new users get started.

.. literalinclude:: ../../template/basic_template.py
  :linenos:



***********************************************************************************************************************	     
HDLRegression()
***********************************************************************************************************************	     

This command is used for initializing the HDLRegression object which is used for defining the regression script
and accessing the HDLRegression API.

The default simulator is Modelsim, but this can be changed by using the ``simulator`` argument as shown 
in example 2 or using :doc:`cli` :

.. code-block:: python

   HDLRegression(<simulator>)


+-----------------+---------------+-------------------------------+---------------+---------------+
| Argument        | Type          | Example                       | Default       | Required      |
+=================+===============+===============================+===============+===============+
| simulator       | string        | "ghdl", "modelsim", "nvc"     | "modelsim"    | optional      |
+-----------------+---------------+-------------------------------+---------------+---------------+
| arg_parser      | argparser obj | regression_parser             | None          | optional      |
+-----------------+---------------+-------------------------------+---------------+---------------+


**Example 1:**

.. code-block:: python

  1. hr = HDLRegression()

  2. hr = HDLRegression(simulator="ghdl")


An argparser object can be created in the regression script and passed on to the HDLRegression() object creation to allow
for having local argument parsing in the regression script. When an argparser object is passed on to HDLRegression it will
add all its arguments to the argparser object. The parsed arguments can be collected using the `get_args()`_ method as show
in example 2.

**Example 2:**

.. code-block:: python

  import argparse
  from hdlregression import HDLRegression
  
  arg_parser = argparse.ArgumentParser(description='Regression script parser')
  arg_parser.add_argument('--rtl', action='store_true', help='run RTL simulations')
  arg_parser.add_argument('--netlist', action='store_true', help='run netlist simulations')
  
  hr = HDLRegression(arg_parser=arg_parser)
  
  args = hr.get_args()
  if args.rtl:
    # add rtl files
    hr.add_files(...)
  if args.netlist:
    # add netlist files
    hr.add_files(...)

  hr.start()



***********************************************************************************************************************	     
Basic methods
***********************************************************************************************************************	     


add_files()
=======================================================================================================================

| Specifies a single or set of files that will be associated with a library name. 
| The library name can be selected explicitly using the ``library_name`` argument or by first setting a library name 
  using the `set_library()`_ method and then omitting the ``library_name`` argument from the ``add_files()`` method.
  See example 2 and 3 below for different approaches to setting library names.
| For VHDL, the files are compiled to the ``library_name`` library, thus the ``library_name`` will need to correspond 
  with the library name used in the design or test environment files.

Files can be referenced with the relative and absolute paths, and the `add_files()`_ method
can be called several times in the regressions script, addressing the same or a different library name.


.. code-block:: python

  add_files(<filename>, <library_name>, <hdl_version>, <com_options>, <netlist_inst>, <code_coverage>)

  add_files(<filename>) 


+--------------------+-----------+---------------+---------------+
| Argument           | Type      | Default       | Required      |
+====================+===========+===============+===============+
| filename           | string    |               | **mandatory** |
+--------------------+-----------+---------------+---------------+
| library_name       | string    | "my_work_lib" | optional      |
+--------------------+-----------+---------------+---------------+
| hdl_version        | string    | 2008          | optional      |
+--------------------+-----------+---------------+---------------+
| com_options        | string    |               | optional      |
+--------------------+-----------+---------------+---------------+
| parse_file         | boolean   | True          | optional      |
+--------------------+-----------+---------------+---------------+
| netlist_inst       | string    |               | optional      |
+--------------------+-----------+---------------+---------------+
| code_coverage      | boolean   |               | optional      |
+--------------------+-----------+---------------+---------------+


**Example 1:**

.. code-block:: python

  hr.add_files("../src/my_testbench.vhd", "my_testbench_lib", hdl_version='2008')

  hr.add_files("../backend/my_design.sdf", "my_design_lib", hdl_version='2008', netlist_inst='/my_testnech/i_test_harness/i_dut')

  hr.add_files("../src/*.vhd", code_coverage=True)


**Example 2: with library name**

.. code-block:: python

  hr.add_files(filename="c:/tools/uvvm/uvvm_util/src/*.vhd", library_name="uvvm_util")
  
  hr.add_files(filename="c:/project/design/src/*.vhd", library_name="design_lib")
  hr.add_files(filename="c:/project/design/src/ip/*.vhd", library_name="design_lib")
  
  hr.add_files(filename="c:/project/design/tb/*.vhd", library_name="test_lib")


**Example 3: with set_library()**

.. code-block:: python

  hr.set_library(library_name="uvvm_util")
  hr.add_files(filename="c:/tools/uvvm/uvvm_util/src/*.vhd")
  
  hr.set_library(library_name="design_lib")
  hr.add_files(filename="c:/project/design/src/*.vhd")
  hr.add_files(filename="c:/project/design/ip/src/*.vhd")
  
  hr.set_library(library_name="test_lib")
  hr.add_files(filename="c:/project/design/tb/*.vhd")


.. include:: file_reference_note.rst


.. note::

  A back annotated timing file (SDF) require the ``netlist_inst`` arguments and a back annotated timing file (VHD)
  require the ``parse_file`` argument set to ``True``.

  #. The ``netlist_inst`` argument is a string that has to be set to design instantiation path in the design.
  #. Any number of back-annotated timing files can be added.


.. note::

  The ``code_coverage`` argument enables code coverage for a single file if an explicit filename is given, or
  a set of files when used with wildcards in the filename.

  It is required that the `set_code_coverage()`_ method is used to set the code coverage settings.

.. warning::

  When ``parse_file`` is set to ``False`` HDLRregression will not parse the file content, not include the file in the
  compilation order and not compile the file.


.. include:: wildcards_reference_tip.rst


set_library()
=======================================================================================================================


Changes the default library name used when `add_files()`_ is used without the ``library_name`` argument. 


.. code-block:: python

  set_default_library(<library_name>)

+-----------------+-----------+---------------+
| Argument        | Type      | Required      | 
+=================+===========+===============+
| library_name    | string    | **mandatory** |
+-----------------+-----------+---------------+

**Example:**

.. code-block:: python

  hr.set_library("testbench_lib")


.. note::

  The default library name is *"my_work_lib"*.




start()
=======================================================================================================================

| This method will initiate compilation, simulation, reporting etc. 
| After calling this method, adding files or making changes to simulation configurations in the regression script
| is not permitted. Ensure that all necessary files and configurations are set before invoking the method to avoid
| issues during the simulation process.


**Return code**

The return code from the start() method is either 0 or 1, based on whether the success criteria listed below are met:

+------------------------------------------------------------------+-------------+
| Criteria                                                         | Return code |
+==================================================================+=============+
| No compilation error and testcase(s) has been run without errors | 0           |
+------------------------------------------------------------------+-------------+
| No compilation error and no testcase run                         | 1           |
+------------------------------------------------------------------+-------------+
| No compilation error and testcase run with one or more errors    | 1           |
+------------------------------------------------------------------+-------------+
| Compilation error (no testcases will be run)                     | 1           |
+------------------------------------------------------------------+-------------+

**Arguments**

The default operation is to run in :ref:`regression mode <What is regression testing>` without :doc:`GUI <gui>` enabled, 
yet this can be changed using the available arguments or by using the :doc:`command line interfaces <cli>`.

.. code-block:: python

  start(<gui_mode>, <stop_on_failure>, <regression_mode>, <threading>, <sim_options>, <netlist_timing>)

+------------------------------+-----------------------+---------------+---------------+
| Argument                     | Options & Type        | Default       | Required      |
+==============================+=======================+===============+===============+
| gui_mode                     | True/False (boolean)  | False         | optional      |
+------------------------------+-----------------------+---------------+---------------+
| regression_mode              | True/False (boolean)  | True          | optional      |
+------------------------------+-----------------------+---------------+---------------+
| stop_on_failure              | True/False (boolean)  | False         | optional      |
+------------------------------+-----------------------+---------------+---------------+
| threading                    | True/False (boolean)  | False         | optional      |
+------------------------------+-----------------------+---------------+---------------+
| sim_options                  | string/list of string | None          | optional      |
+------------------------------+-----------------------+---------------+---------------+
| netlist_timing               | string                | None          | optional      |
+------------------------------+-----------------------+---------------+---------------+
| keep_code_coverage           | True/False (boolean)  | False         | optional      |
+------------------------------+-----------------------+---------------+---------------+
| no_default_com_options       | True/False (boolean)  | False         | optional      |
+------------------------------+-----------------------+---------------+---------------+
| ignore_simulator_exit_codes  | list of int           | []            | optional      |
+------------------------------+-----------------------+---------------+---------------+


**Example:**

.. code-block:: python

  hr.start(gui_mode=True, threading=True)

  hr.start(netlist_timing='-sdfmin')



.. note::

  * | ``gui_mode`` selects if simulations should be run from terminal or inside :doc:`GUI <gui>` - if supported by the simulator. 
    | In GUI the simulator is started with predefined HDLRegression methods that simplyfies compilation and running tests.

  * ``regression_mode`` selects run method, i.e. only run tests that:
  
    #. have not previously been run
    #. have not passed
    #. are affected by file changes and need to be rerun.

  * ``stop_on_failure`` selects if the regression run shall continue running if a test fails.

  * ``threading`` selects if tasks are run in parallel. Depending on the workload this can decrease run time of some
    regression runs.

  * ``sim_options`` adds extra commands to simulator executor call.

  * ``netlist_timing`` is a string that has to be set to "-sdfmin", "-sdftyp" or "-sdfmax".
  
  * ``keep_code_coverage`` will keep code coverage results from a previous test run. This can be useful in situations where 
    a subset of tests needs to be rerun to achieve wanted code coverage.   
    
  * ``no_default_com_options`` disables preconfigured settings for disabling the following warnings:
  
    #. vcom-1236: shared variables must be of a protected type
    #. vcom-1346: default expression of interface object is not globally static
    #. vcom-1090: possible infinite loop: process contains no WAIT statement
  


.. warning::

  **gui_mode** will run testcases in one of these modes:
  
  #. testcases added by the `add_testcase()`_ method or using the :doc:`command line interfaces <cli>`.
 
  #. regression mode.

  starting with bullet point 1, and if no testcases have been added, moving on to bullet point 2. 


***********************************************************************************************************************	     
Advanced methods
***********************************************************************************************************************	     


add_generics()
=======================================================================================================================

Selects the generics to be used when running a testcase.
A test run is created when generics are added to a testcase, thus calling `add_generics()`_ two times will create
two test runs. 

.. code-block:: python

  add_generics(<entity>, <architecture>, <generics>)


+-------------------+--------------------------------+---------------+
| Argument          | Type                           | Required      |
+===================+================================+===============+
| entity            | string                         | **mandatory** |
+-------------------+--------------------------------+---------------+
| architecture      | string                         | optional      |
+-------------------+--------------------------------+---------------+
| generics          | list [string, int/string/bool] | **mandatory** |
+-------------------+--------------------------------+---------------+

.. important::

  * | All generics that are used for input or output files inside a testbench 
      will require the ``PATH`` keyword when setting the generic in the regression script. 
    | The generic value and the ``PATH`` keyword has to be of a Python **tuple** type. 
      HDLRegression will make the adjustments for the generic paths to match HDLRegression test paths. See example 3.


**Example:**

.. code-block:: python

  1. hr.add_generics(entity="my_dut_tb", generics=["GC_BUS_WIDTH", 16, "GC_ADDR_WIDTH", 8])
  
  2. hr.add_generics(entity="my_dut_tb", architecture="test", generics=my_generics_list)

  3. hr.add_generics(entity="my_dut_tb", generics=["GC_DATA_FILE", ("../test_data/input_data.txt", "PATH"), "GC_MASTER_MODE", True])

.. include:: file_reference_note.rst


add_precompiled_library()
=======================================================================================================================
Specifies the name and path of a precompiled library.

.. note::

  The library will never be compiled and only a reference is added to the modelsim.ini file.
  Any number of precompiled libraries can be added.

.. code-block:: python

  add_precompiled_library(<compile_path>, <library_name>)


+-----------------+---------------------------+---------------+
| Argument        | Type                      | Required      |
+=================+===========================+===============+
| compile_path    | string                    | **mandatory** |
+-----------------+---------------------------+---------------+
| library_name    | string                    | **mandatory** |
+-----------------+---------------------------+---------------+


add_testcase()
=======================================================================================================================

Adding testcase(s) will configure HDLRegression to only run these testcases. 
All testcases are run if no testcases are added using this command.
Selecting testcase can also be done by using :doc:`command line interfaces <cli>`, and testcases selected from CLI will 
override any scripted testcase selecition.


.. important::
  A testcase name is a string that consists of 
  
  #. testbench entity name
  #. testbench architecture name
  #. test name (optional)

  And where the three testcase name elements are separated by a dot (``.``): ``<testbench_name>.<architecture_name>.<test_name>``.


.. include:: wildcards_reference_tip.rst


.. code-block:: python

  add_testcase(<testcase>)


+-------------------+---------------------------+---------------+
| Argument          | Type                      | Required      |
+===================+===========================+===============+
| *testcase*        | string / list of strings  | **mandatory** |
+-------------------+---------------------------+---------------+


**Example:**

.. code-block:: python

  add_testcase("interface_tb.test_arch.read_test") # this test only

  add_testcase("interface_tb.*.read_*") # all architectures and all sequencer testcases starting with 'read'

  add_testcase("interface_tb.test_arch.????_test") # all sequencer testcases mathing any 4 character start, followed by '_test'

  add_testcase(interface_tests_list) # a list of selected tests


.. note::

  The `start()`_ method will return error code 1 if no testcases matched the ``testcase`` keyword.
  


add_to_testgroup()
=======================================================================================================================


| Will add tests to a collection of tests, i.e. :ref:`test group <Test group>`, that can be run in groups. 
  The test group is given a name that is used for addressing the test collection.
| There are no limit for how many tests that can be added to a test group, and no limit for the number of test groups.
| Running a test group can be done using a :doc:`command line interface <cli>`.


.. code-block:: python

  hr.add_to_testgroup(testgroup_name, entity, architecture=None, testcase=None, generic=[]) 


+-------------------+--------------------------------+---------------+
| Argument          | Type                           | Required      |
+===================+================================+===============+
| testgroup_name    | string                         | **mandatory** |
+-------------------+--------------------------------+---------------+
| entity            | string                         | **mandatory** |
+-------------------+--------------------------------+---------------+
| architecture      | string                         | optional      |
+-------------------+--------------------------------+---------------+
| testcase          | string                         | optional      |
+-------------------+--------------------------------+---------------+
| generic           | list [string, int/string/bool] | optional      |
+-------------------+--------------------------------+---------------+


.. note::

  * ``add_to_testgroup()`` adds existing tests to a collection, i.e. no new tests are created.
  * The ``testcase`` argument is for selecting sequencer built-in testcases.
  * The `start()`_ method will return error code 1 if no test group or testcase were found.


.. include:: wildcards_reference_tip.rst



compile_uvvm()
=======================================================================================================================
  
Compiles UVVM to HDLRegression library folder, making UVVM available to all tests run by HDLRegression.
  
.. code-block:: python
  
  hr.compile_uvvm(<path_to_uvvm>)
  
+-------------------+-----------------------------------+---------------+
| Argument          | Example                           | Required      |
+===================+===================================+===============+
| path_to_uvvm      | "../ip/UVVM"                      | **mandatory** |
+-------------------+-----------------------------------+---------------+
  
**Example:**
  
.. code-block:: python
  
  hr.compile_uvvm("c:/development/tools/UVVM")


.. important::

  * The UVVM path has to absolute or relative to the regression script location.


compile_osvvm()
=======================================================================================================================
  
Compiles OSVVM to HDLRegression library folder, making OSVVM available to all tests run by HDLRegression.
  
.. code-block:: python
  
  hr.compile_osvvm(<path_to_osvvm>)
  
+-------------------+-----------------------------------+---------------+
| Argument          | Example                           | Required      |
+===================+===================================+===============+
| path_to_osvvm     | "../ip/OSVVM"                     | **mandatory** |
+-------------------+-----------------------------------+---------------+
  
**Example:**
  
.. code-block:: python
  
  hr.compile_osvvm("c:/development/tools/OSVVM")


.. important::

  * The OSVVM path has to absolute or relative to the regression script location.


configure_library()
=======================================================================================================================

Set special settings for a library that differs significantly from the regular settings.

.. code-block:: python

  hr.configure_library(<library>, <never_recompile>, <set_lib_dep>)

+-------------------+---------------------------------------+-----------------------------------+---------------+
| Argument          | Options                               | Example                           | Required      |
+===================+=======================================+===================================+===============+
| library           | *library name* (string)               | "can_ip_library"                  | **mandatory** |
+-------------------+---------------------------------------+-----------------------------------+---------------+
| never_recompile   | True/False (boolean)                  | True                              | optional      |
+-------------------+---------------------------------------+-----------------------------------+---------------+
| set_lib_dep       | *library name* (string)               | "ip_library"                      | optional      |
+-------------------+---------------------------------------+-----------------------------------+---------------+

**Example:**

.. code-block:: python

  hr.configure_library(library='can_ip_library', never_recompile=True)




gen_report()
=======================================================================================================================

Writes a test run report file to the ``hdlregression/test`` folder. The default report file is ``report.txt`` 
and can be changed using the ``report_file`` argument. The report file is saved in the ``/hdlregression/test`` folder, thus no path 
should be given to the report name.

.. code-block:: python

  gen_report(<report_file>, <compile_order>, <library>)


+-------------------+---------------------------+---------------+---------------+
| Argument          | Options & Type            | Default       | Required      |
+===================+===========================+===============+===============+
| report_file       | *filename* (string)       | "report.txt"  | optional      |
+-------------------+---------------------------+---------------+---------------+
| compile_order     | True / False (boolean)    | False         | optional      |
+-------------------+---------------------------+---------------+---------------+
| library           | True / False (boolean)    | False         | optional      |
+-------------------+---------------------------+---------------+---------------+

**Example:**

.. code-block:: python

  hr.gen_report(report_file="sim_report.csv", compile_order=True)
  hr.gen_report(report_file="sim_report.csv", compile_order=True, library=True)


.. important::

  Supported file types are ``.txt``, ``.csv`` and ``.json`` and the file type is extracted from the file name.




get_args()
=======================================================================================================================

The command is used for getting the parsed arguments from HDLRegression.
This method can be used when there is a argparser object that is created in the regression script.
See `HDLRegression()`_ example 2 for usage.


**Example:**

.. code-block:: python

  args = hr.get_args()



get_file_list()
=======================================================================================================================

The command is used for reading back the files added to the libraries in HDLRegression.
All files from all libraries are returned in a list.


**Example:**

.. code-block:: python

  file_list = hr.get_file_list()



remove_file()
=======================================================================================================================

Removes a file that has been added to a library, e.g. after using ``add_files()`` with asterix for adding several files.


.. code-block:: python

  remove_file(<filename>, <library_name>)


+--------------------+-----------+---------------+
| Argument           | Type      | Required      |
+====================+===========+===============+
| filename           | string    | **mandatory** |
+--------------------+-----------+---------------+
| library_name       | string    | **mandatory** |
+--------------------+-----------+---------------+


**Example:**

.. code-block:: python

  hr.add_files("../src/*.vhd", "testbench_lib")
  hr.remove_file("unused_file.vhd", "testbench_lib")
  hr.start()


.. note::
  
  The filename can not include the path to the file or any wildcards.



run_command()
=======================================================================================================================

The command is executed by HLDRegression at the given stage in the regression script. I.e. pre-simulation commands will have 
to be called prior to `start()`_ and post-simulation commands need to be called after `start()`_.

.. code-block:: python

  hr.run_command(<command>)


+-------------------+---------------------------+---------------+
| Argument          | Type                      | Required      |
+===================+===========================+===============+
| command           | string                    | **mandatory** |
+-------------------+---------------------------+---------------+
| verbose           | boolean                   | optional      |
+-------------------+---------------------------+---------------+


.. note::
  No output is printed to the terminal by default, but this can
  be changed by setting the ``verbose`` argument to ``True``.

**Example:**

.. code-block:: python
  
  hr.run_command('python3 ../script/run_spec_cov.py --config ../script/config.txt')

  hr.run_command('vsim -version', verbose=True)


.. include:: file_reference_note.rst



set_code_coverage()
=======================================================================================================================
  
Sets the code coverage settings used when running the tests.
  
.. code-block:: python
  
  hr.set_code_coverage(<code_coverage_settings>, <code_coverage_file>, <exclude_file>, <merge_options>)
  
+------------------------+---------------+-------------------+---------------+
| Argument               | Type          | Example           | Required      |
+========================+===============+===================+===============+
| code_coverage_settings | string        | "bcst"            | **mandatory** |
+------------------------+---------------+-------------------+---------------+
| code_coverage_file     | string        | "coverage.ucdb"   | **mandatory** |
+------------------------+---------------+-------------------+---------------+
| exclude_file           | string        | "exceptions.tcl"  | optional      |
+------------------------+---------------+-------------------+---------------+
| merge_options          | string        | "-testassociated" | optional      |
+------------------------+---------------+-------------------+---------------+


.. note::
  
  * `add_files()`_ require the ``code_coverage`` argument enabled for every file that should sample code coverage.
  * Each test run will generate a ``code_coverage_file`` inside its test folder.
  * Results from the regression are accumulated in a ``code_coverage_file`` ``_merge`` file inside the 
    ``test/coverage/`` folder.
  * Exceptions are filtered from the accumulated file automatically in a ``code_coverage_file`` ``_filter`` file
    inside the ``test/coverage/`` folder.
  * Reports are written to the ``test/coverage/txt`` and ``test/coverage/html`` folders using the filtered 
    exception results if a ``exlude_file`` is set, or using the merged code coverage results if no ``exclude_file`` is set.
  * Only the current test run is used for code coverage, meaning that a full regression run is required to sample 
    code coverage for the complete test suite.



**Example:**
  
.. code-block:: python
  
  hr.set_code_coverage("bcst", "code_coverage.ucdb")

  hr.set_code_coverage("bcst", "code_coverage.ucdb", "exclude.tcl")



set_dependency()
=======================================================================================================================

Specifies the libraries that have a dependency to the ``library_name`` library, and ensures that ``library_name`` is 
compiled after all of the libraries listed in ``dep_library``.

.. code-block:: python

  set_dependency(<library_name>, <dep_library>)

+-----------------+---------------------------+---------------+
| Argument        | Type                      | Required      |
+=================+===========================+===============+
| library_name    | string                    | **mandatory** |
+-----------------+---------------------------+---------------+
| dep_library     | list [string]             | **mandatory** |
+-----------------+---------------------------+---------------+


.. note::

  #. Specifying the library dependency is usually not necessary as HDLRegression is capable of detecting dependencies. 
  #. ``dep_library`` list has to be a list of library name(s).





set_result_check_string() 
=======================================================================================================================

The result of a test run is determined by scanning the simulation log file, searching after a specific string.
If the string is found the test run is set as **PASS**, and **FAIL** otherwise, thus only a passing test should
report the check string.

.. code-block:: python

  set_result_check_string(<check_string>)


+-------------------+-------------------------+---------------+
| Argument          | Type                    | Required      |
+===================+=========================+===============+
| check_string      | string                  | **mandatory** |
+-------------------+-------------------------+---------------+


.. note::
  The default test pass string is the UVVM ``report_alert_counters(FINAL)`` summary, with ``SUCCESS`` as 
  criteria for a passing test.


**Example:**

.. code-block:: python

  hr.set_result_check_string("testcase passed")


.. literalinclude:: examples/example_tb_result.vhd
  :caption: Example TB with testcase result string
  :linenos:
  :language: vhdl




set_simulator()
=======================================================================================================================

HDLRegression is configured to run using Modelsim and VHDL version 2008 as default. This method allows for changing

* Simulator
* Simulator executable path
* Simulator com_options

| This can be useful when the test script should be run with a different version of Modelsim other than the 
  one listed in the system path, where all that is needed is to change the path for the Modelsim executable.
| It is also possible to select simulator when initializing the :ref:`HDLRegression <HDLRegression()>` object, but without selecting 
  compile options and setting simulator executable path, or by using :doc:`command line interfaces <cli>`.


.. code-block:: python

  set_simulator(<simulator>, <simulator_path>, <com_options>)

+-------------------+---------------------------------------------+-----------------------------------+---------------+---------------+
| Argument          | Options                                     | Example                           | Default       | Required      |
+===================+=============================================+===================================+===============+===============+
| simulator         | *simulator name* (string)                   | "MODELSIM", "GHDL", "NVC"         | "MODELSIM"    | **mandatory** |
+-------------------+---------------------------------------------+-----------------------------------+---------------+---------------+
| simulator_path    | *simulator_executable_path* (string)        | "c:/ghdl/bin"                     |               | optional      |
+-------------------+---------------------------------------------+-----------------------------------+---------------+---------------+
| com_options       | *compile optionss* (string/list of string)  | "-suppress 1346,1236,1090 -2008"  |               | optional      |
+-------------------+---------------------------------------------+-----------------------------------+---------------+---------------+

**Example:**

.. code-block:: python

  hr.set_simulator(simulator="GHDL")

  hr.set_simulator(simulator="MODELSIM", path='c:/tools/intelFPGA/20.1/modelsim_ase/win32aloem')


.. important::

  All path slashes has to be written as forward slash / .


.. include:: file_reference_note.rst




set_testcase_identifier_name()
=======================================================================================================================

Sets the name of the testcase generic used when defining several testcases 
inside a single testbench architecture. The default testcase generic is ``GC_TESTCASE``,
but any name can be given.

.. note::
  * The sequencer built-in testcase if-structure will need to match this generic.
  * HDLRegression extracts all the sequencer built-in testcases based on the combined usage of this generic 
    and if-matched strings.

.. code-block:: python

  hr.set_testcase_identifier_name(<testcase_id>)


+-------------------+---------------------------+---------------+
| Argument          | Type                      | Required      |
+===================+===========================+===============+
| testcase_id       | string                    | **mandatory** |
+-------------------+---------------------------+---------------+


**Example:**

.. code-block:: python

  hr.set_testcase_identifier_name("GC_TESTCASE")


.. literalinclude:: examples/example_tb_generic.vhd
  :caption: Example TB with testcase ID generic
  :linenos:
  :language: vhdl




***********************************************************************************************************************	     
Statistical methods
***********************************************************************************************************************	     


get_results()
=======================================================================================================================

Returns a list of all passed, failed and not run tests.

.. code-block:: python

  hr.get_results()


**Example:**

.. code-block:: python

  result_list = hr.get_results()

  passed_tests = result_list[0]
  failed_tests = result_list[1]
  not_run_tests = result_list[2]



.. code-block:: python

  (passed_tests, failed_tests, not_run_tests) = hr.get_results()



get_num_tests_run()
=======================================================================================================================

Returns the number of tests run.

.. code-block:: python

  hr.get_num_tests_run()


**Example:**

.. code-block:: python

  num_tests = hr.get_num_tests_run()



get_num_pass_tests()
=======================================================================================================================

Returns the number of passed test runs.

.. code-block:: python

  hr.get_num_pass_tests()


**Example:**

.. code-block:: python

  num_passed_tests = hr.get_num_pass_tests()



get_num_fail_tests()
=======================================================================================================================

Returns the number of failed test runs.

.. code-block:: python

  hr.get_num_fail_tests()


**Example:**

.. code-block:: python

  num_failed_tests = hr.get_num_fail_tests()



get_num_pass_with_minor_alert_tests()
=======================================================================================================================

Returns the number of passed test runs that completed with minor alerts.

.. note::

  This is only applicable for tests run with the UVVM verification framework.


.. code-block:: python

  hr.get_num_pass_with_minor_alert_tests()


**Example:**

.. code-block:: python

  num_passed_tests_with_minor_alerts = hr.get_num_pass_with_minor_alert_tests()
