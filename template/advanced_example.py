from itertools import product
from hdlregression import HDLRegression
import sys
# User specify HDLRegression install path:
sys.path.append('c:/tools/hdlregression/')

# Import the HDLRegression module to the Python script:

# Import other Python package(s):


# Define a HDLRegression item to access the HDLRegression functionality:
hr = HDLRegression()

# ------------ USER CONFIG START ---------------

# Add Python functions here if needed:

# Return a list with the product of the generics


def create_generics(bus_width, master_mode, input_file, output_file):
    generics = []
    for bus_width, master_mode, input_file, output_file in product(bus_width, master_mode, input_file, output_file):
        generics.append(["GC_BUS_WIDTH",bus_width, "GC_MASTER_MODE",master_mode, "GC_INPUT_FILE",input_file, "GC_OUTPUT_FILE",output_file])
    return generics


# Add all source files to library my_dut_lib:
hr.add_files("./src/*.vhd", "my_dut_lib")


# Add all testbench related files to library my_tb_lib:
hr.set_library("my_tb_lib")
hr.add_files("./tb/my_dut_tb.vhd")
hr.add_files("./tb/my_dut_th.vhd")
hr.add_files("./tb/my_dut_if_stuck_tb.vhd")
hr.add_files("./tb/my_dut_pin_pulse_tb.vhd")


# Get a list with the product of selected generics:
generics = create_generics(bus_width=[2, 4, 8, 16], master_mode=[
                           True, False], input_file="in_data.txt", output_file="out_data.txt")

# Add generics for testbench run:
hr.add_generics(entity="my_dut_tb", generics=generics)

# Specify output report as CSV:
hr.gen_report(report_file="project_report.csv")

# ------------ USER CONFIG END ---------------
hr.start(regression_mode=True)
