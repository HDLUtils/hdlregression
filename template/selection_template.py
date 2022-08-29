import sys
# ----------- USER HDLRegression PATH -----------------
# If HDLRegression is not installed as a Python package (see doc)
# then uncomment the following line and set the path for
# the HDLRegression install folder :
#sys.path.append(<full_or_relative_path_to_HDLRegression_install>)

# Import the HDLRegression module to the Python script:
from hdlregression import HDLRegression


def run_rtl():
    '''
    Setup test environment for RTL simulations.
    '''
    # Define a HDLRegression item to access the HDLRegression functionality:
    hr = HDLRegression()

    # ------------ USER CONFIG START ---------------
    # => hr.add_files(<filename>)                   # Use default library my_work_lib
    # => hr.add_files(<filename>, <library_name>)   # or specify a library name.

    # ------------ USER CONFIG END ---------------
    hr.start()



def run_netlist():
    '''
    Setup test environment for Netlist simulations.
    '''
    # Define a HDLRegression item to access the HDLRegression functionality:
    hr = HDLRegression()

    # ------------ USER CONFIG START ---------------
    # => hr.add_files(<filename>)                   # Use default library my_work_lib
    # => hr.add_files(<filename>, <library_name>)   # or specify a library name.

    # ------------ USER CONFIG END ---------------
    hr.start()


def main():
    '''
    Main method, selecting RTL or Netlist simulations.
    '''

    args = sys.argv[1:]

    if len(args) > 0:
        selection = args[0].lower()
        sys.argv.remove(selection)

        if 'rtl' == selection:
            run_rtl()
        elif 'netlist' == selection:
            run_netlist()
        else:
            print('Please select "rtl" or "netlist" run.')
    else:
        print('Please select "rtl" or "netlist" run.')


if __name__ == "__main__":
    main()
