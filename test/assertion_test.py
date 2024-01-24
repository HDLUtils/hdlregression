import sys

# ----------- USER HDLRegression PATH -----------------
# If HDLRegression is not installed as a Python package (see doc)
# then uncomment the following line and set the path for
# the HDLRegression install folder :
# sys.path.append(<full_or_relative_path_to_hdlregression_install>)

# Import the HDLRegression module to the Python script:
from hdlregression import HDLRegression

# Define a HDLRegression item to access the HDLRegression functionality:
hr = HDLRegression()

# ------------ USER CONFIG START ---------------
hr.add_files("dut/dut_assertion.vhd", "assertion_lib")
hr.add_files("tb/tb_assertion.vhd", "assertion_lib")

hr.set_result_check_string("TC done")

# ------------ USER CONFIG END ---------------
hr.start()
