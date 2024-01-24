
#######################################################################################################################
Generated output
#######################################################################################################################

When a HDLRegression regression script is run a folder `hdlregression` will be created in the same folder as the script was called
from, e.g. `sim`. The folder will hold important project information in `.dat` files, a list of all run commands inside
a `commands.do` file, library compilations inside a `library` folder, and test run outputs and report information inside
a `test` folder. Note that each time the regression script is run it will back-up the `test` folder with a date-and-time
suffix to ensure that no important test run results are overwritten.

* /library
* /test
* commands.do
* library.dat
* settings.dat
* testgroup.dat
* testgroup_collection.dat

.. note::
    
    The library folder will include one or more folders for the compiled libraries.
    The test folder will include one or more testcase folders and - if selected - a coverage folder.


***********************************************************************************************************************	     
Test folder
***********************************************************************************************************************	     


Inside thet `/test` folder there can be several sub-folders and files. Each testbench entity will have a folder of its own 
which again has sub-folders for used architecture and generics. These `test run` folders have unique names that are
hash generated, thus identifying a specific test run can be done by inspecting the test mapping file, `test_mapping.csv`.


.. literalinclude:: tree_output.txt
  :caption: HDLRegression output folder example
  :linenos:
  :language: console


Test mapping
=======================================================================================================================

A test mapping file `test_mapping.csv` is located in every `test` folder to help identify test runs with test
output folders. An example of the layout of a test mapping file is shown below:


.. code-block:: console
    :caption: test_mapping.csv example
        
    1, ./hdlregression/test/irqc_demo_tb/func_1, bitvis_irqc.irqc_demo_tb(func)
    2, ./hdlregression/test/irqc_tb/func_2, bitvis_irqc.irqc_tb(func)
    3, ./hdlregression/test/uart_vvc_demo_tb/func_3, bitvis_uart.uart_vvc_demo_tb(func)
    4, ./hdlregression/test/uart_simple_bfm_tb/func_4, bitvis_uart.uart_simple_bfm_tb(func)
    5, ./hdlregression/test/uart_vvc_tb/func_5, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=check_register_defaults
    6, ./hdlregression/test/uart_vvc_tb/func_6, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=check_simple_transmit
    7, ./hdlregression/test/uart_vvc_tb/func_7, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=check_simple_receive
    8, ./hdlregression/test/uart_vvc_tb/func_8, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=check_single_simultaneous_transmit_and_receive
    9, ./hdlregression/test/uart_vvc_tb/func_9, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=check_multiple_simultaneous_receive_and_read
    10, ./hdlregression/test/uart_vvc_tb/func_10, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=skew_sbi_read_over_uart_receive
    11, ./hdlregression/test/uart_vvc_tb/func_11, bitvis_uart.uart_vvc_tb(func):GC_TESTCASE=skew_sbi_read_over_uart_receive_with_delay_functionality

  
