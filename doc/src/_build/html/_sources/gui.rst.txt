
#######################################################################################################################
Graphical User Interface (GUI)
#######################################################################################################################

Sometimes debugging a design or test require the use of GUI (graphical user interface) 
and HDLRegression can run tests in GUI when called with the ``-g`` or ``--gui`` arugument.
When enabled, the regression script will open inside Modelsim GUI with a loaded testcase ready to run.


.. code-block:: console

  > python ../test/regression.py -tc uart_vvc_tb.func.check_simple_transmit -g


HDLRegression in GUI mode provides a set of functions for compiling and running a 
test:

.. image:: images/gui_menu.png
  :width: 550
  :name: GUI menu
  :align: center