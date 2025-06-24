
#######################################################################################################################
Graphical User Interface (GUI)
#######################################################################################################################

Modelsim
--------

Sometimes debugging a design or test require the use of GUI (graphical user interface) 
and HDLRegression can run tests in GUI when called with the ``-g`` or ``--gui`` arugument.
When enabled, the regression script will open inside ModelSim/QuestaSim/Rivier-PRO GUI with a loaded testcase ready to run.


.. code-block:: console

  > python ../test/regression.py -tc uart_vvc_tb.func.check_simple_transmit -g


HDLRegression in GUI mode provides a set of functions for compiling and running a 
test:

.. image:: images/gui_menu.png
  :width: 550
  :name: GUI menu
  :align: center
  

GHDL / NVC
----------

GHDL and NVC does not have a GUI, but can create simulation waveform files that can be opened to have a graphical representation
of the signals in a VCD format (Value Change Dump).

When HDLRegression is called with GUI arguments and runnning with GHDL/NVC simulator it will create ``sim.vcd`` files
inside every testcase run folder. The VCD files can then be opened in a graphical wavefarm viewer such as GTKWave.


.. code-block:: console

  > python ../test/regression.py -tc uart_vvc_tb.func.check_simple_transmit -g -s ghdl
  > gtkwave ./hdlregression/test/uart_vvc_tb/54005228/sim.vcd &

