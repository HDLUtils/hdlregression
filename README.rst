HDLRegression
=============

**HDLRegression** is a user-friendly Python3-based regression test runner designed to simplify
and accelerate the FPGA verification workflow. HDLRegression is perfect for everything from small FPGA modules
to large FPGA projects, and will fit into an existing setup, minimizing both setup time and complexity.

**HDLRegression is all about simplicity and efficiency:** Quick setup, minimal changes, maximum productivity.

Benefits of using HDLRegression
-------------------------------

✅ **Fast Integration:** Easily adapt your existing verification environment.

✅ **Easy Configuration:** Replace TCL scripts or Makefiles with simple Python3 scripts.

✅ **Efficient Workflow:** Run simulations locally or in Continuous Integration (CI) environments.

Getting Started in 3 Easy Steps
-------------------------------

Integrating HDLRegression into an existing FPGA verification workflow is straightforward:


📌 **Step 1: Prepare Testbench**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mark testbench entities with an HDLRegression comment:

.. code-block:: vhdl

   -- hdlregression:tb
   entity foo_tb is
   end entity;

HDLRegression will work with most verification frameworks.


📌 **Step 2: Configure Simulation Script**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Set up a simple Python script (e.g. `run_sim.py`) in the project's directory:

.. code-block:: python

   from hdlregression import HDLRegression

   hr = HDLRegression()
   hr.add_files("src/", "design_lib")   # Path to your design files
   hr.add_files("tb/", "tb_lib")        # Path to your testbench files

   hr.start()


📌 **Step 3: Run Simulations**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start the simulations:

.. code-block:: bash

   python run_sim.py

HDLRegression compiles, runs, and reports the results automatically.


Documentation
-------------

📚 Documentation (PDF, HTML, and RST) can be found in the ``/doc`` directory.


Installation
------------

Install HDLRegression using pip:

.. code-block:: bash

   python -m pip install -e .

Or, manually add HDLRegression in regression script:

.. code-block:: python

   import sys
   sys.path.append("<path_to_hdlregression_folder>")


Contributing
------------

🤝 HDLRegression is open-source and welcomes contributions. Submit your ideas, bug reports,
or improvements via GitHub issues or pull requests.


License
=======

This project is licensed under the MIT License - see the LICENSE file for details.