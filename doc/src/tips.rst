.. role:: bash(code)
   :language: bash

#######################################################################################################################
Tips
#######################################################################################################################


***********************************************************************************************************************	     
Back annotated netlist simulations
***********************************************************************************************************************	     

Running RTL and Netlist simulations require two individual test runs, i.e. different HDLRegression instances, and solving
this can be done using one or two regression scripts:

* Use two run scripts, e.g. ``run_rtl.py`` and ``run_netlist.py``, and setup both scripts as individual runs, 
  one running RTL simulations and the other running Netlist simulations. 

* Combine both run scripts in a single file, e.g. ``run_regression.py``, and use a selection mechanism inside the
  run script to select which run to execute.


.. note::

   The single runner script example will support HDLRegression CLI arguments when implemented with 
   argument modifications as shown in the example below.


Regression script
=======================================================================================================================

**Example of running RTL and Netlist from two runner scripts**

.. code-block:: python

   python3 ../script/run_rtl.py

   python3 ../script/run_netlist.py


**Example of running RTL and Netlist from a single runner script**

.. code-block:: python

   python3 ../script/run_regression.py rtl

   python3 ../script/run_regression.py netlist


**Example setup for running RTL and Netlist from a single runner script**

.. literalinclude:: ../../template/selection_template.py
  :linenos:


