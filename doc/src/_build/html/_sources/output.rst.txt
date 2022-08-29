
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
        
    ./hdlregression/test/uart_simple_bfm_tb/70910381, bitvis_uart.uart_simple_bfm_tb(func)
    ./hdlregression/test/uart_vvc_tb/1419120764, bitvis_uart.uart_vvc_tb(func): gc_testcase=check_register_defaults
    ./hdlregression/test/uart_vvc_tb/886640571, bitvis_uart.uart_vvc_tb(func): gc_testcase=check_simple_transmit
    ./hdlregression/test/uart_vvc_tb/613945132, bitvis_uart.uart_vvc_tb(func): gc_testcase=check_simple_receive
    ./hdlregression/test/uart_vvc_tb/1155471887, bitvis_uart.uart_vvc_tb(func): gc_testcase=check_single_simultaneous_transmit_and_receive
    ./hdlregression/test/uart_vvc_tb/301996323, bitvis_uart.uart_vvc_tb(func): gc_testcase=check_multiple_simultaneous_receive_and_read
    ./hdlregression/test/uart_vvc_tb/3913552845, bitvis_uart.uart_vvc_tb(func): gc_testcase=skew_sbi_read_over_uart_receive
    ./hdlregression/test/uart_vvc_tb/1589059134, bitvis_uart.uart_vvc_tb(func): gc_testcase=skew_sbi_read_over_uart_receive_with_delay_functionality
    ./hdlregression/test/uart_vvc_demo_tb/70910381, bitvis_uart.uart_vvc_demo_tb(func)

  
