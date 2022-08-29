import sys
# User specify HDLRegression install path:
sys.path.append('c:/tools/hdlregression/')

# Import the HDLRegression module to the Python script:
from hdlregression import HDLRegression

# Define a HDLRegression item to access the HDLRegression functionality:
hr = HDLRegression()

# ------------ USER CONFIG START ---------------

# Add all .vhd files in the /src directory to library my_dut_lib:
hr.add_files("./src/*.vhd", "my_dut_lib")

# Add testbech file to library my_tb_lib:
hr.add_files("./tb/my_tb.vhd", "my_tb_lib")

# ------------ USER CONFIG END ---------------
hr.start()