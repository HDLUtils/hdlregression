
#######################################################################################################################
Testbench
#######################################################################################################################

For HDLRegression to extract the correct information from the testbench files, there are some 
code requirements that have to be fulfilled. This information is used by HDLRegression to 
detect 


***********************************************************************************************************************	     
Prerequisites
***********************************************************************************************************************	     

This are the requirements of a HDLRegression supporting testbench:

  - The testbench file has to have the HDLRegression pragma above the entity declaration:

    - Only the top testbench file can have the HDLRegression testbench pragma.
    - Each top level testbench file has to have the HDLRegression testbench pragma.

  - A testbench simulation result report will have to match the :ref:`set_result_check_string()` to 
    **PASS**, and the test run will **FAIL** if this string is not found in the simulation transcript.

    .. note::
    
      UVVM ``report_alert_counters(FINAL)`` is the default method for verifying a passing or failing test, and will have
      to be added to the testbench if no other ``check_string`` is selected. See example testbench for suggested
      implementation.


  **VHDL** testbench

  .. code-block:: vhdl
  
    --HDLRegression:TB
    entity my_dut_tb is


  **Verilog** testbench

  .. code-block:: verilog

    //HDLRegression:TB
    module my_dut_tb;


  .. note::
    
    # A testbench with multiple testcases requires the GC_TESTCASE generic (VHDL) or TESTCASE parameter 
    (Verilog), and these should only be used in the top level testbench entity.
    
    # The testcase names will be included in simulation reports.


  .. code-block:: vhdl
  
    GC_TESTCASE : string := ""  -- VHDL
    parameter TESTCASE = ""     // Verilog


Note that the ``GC_TESTCASE`` generic or ``TESTCASE`` parameter name can be changed using
the :ref:`set_testcase_identifier_name()` method.


***********************************************************************************************************************	     
Example Testbench
***********************************************************************************************************************	     


For HDLRegression to discover a VHDL file to be used as a testbench the only requirement is that
the ``--hdlregression:tb`` (VHDL) or ``//hdlregression:tb`` (Verilog) pragma is present:

.. literalinclude:: examples/example_tb_full.vhd
  :linenos:
  :caption: VHDL testbench example
  :language: vhdl


.. literalinclude:: examples/example_tb_verilog.v
  :linenos:
  :caption: Verilog testbench example
  :language: verilog