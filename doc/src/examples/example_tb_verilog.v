//hdlregression:tb
module tb_verilog #(
        parameter TESTCASE = "DEFAULT"
    );

    initial
    begin
        if (TESTCASE == "reset_test")
            // reset checks

        else if (TESTCASE == "write_test")
            // write tests

        else if (TESTCASE == "read_test")
            // read tests

    end

endmodule