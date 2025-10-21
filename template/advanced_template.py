import sys
# ----------- USER HDLRegression PATH -----------------
# If HDLRegression is not installed as a Python package (see doc)
# then uncomment the following line and set the path for
# the HDLRegression install folder :
#sys.path.append(<full_or_relative_path_to_hdlregression_install>)

# Import the HDLRegression module to the Python script:
from hdlregression import HDLRegression

# ----------- USER IMPORT -----------------
# Import other Python package(s):

# Define a HDLRegression item to access the HDLRegression functionality:
hr = HDLRegression()

# ------------ USER CONFIG START ---------------

# Add Python functions here if needed:

# Add design files, repeat call if needed:
# => hr.add_files(<src_files>, <compile_library>)

# Add testbench and related files:
# => hr.add_files(<src_files>, <compile_library>)

# Define testbench configurations/generics if any, repeat call if needed:
# => hr.add_generics(entity=<testbench_name>, architecture=<architecture_name>, generics=<generics_list>)

# Define simulation report format:
# => hr.gen_report() # default is full report (testbench, testcase, configurations, pass/fail) to report.txt


# ------------ USER CONFIG END ---------------
hr.start()
