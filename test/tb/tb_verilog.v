//HDLRegression:tb
module tb_verilog_testcase #(
        parameter TESTCASE = "DEFAULT"
    );

    initial
    begin
        if (TESTCASE == "testcase_1")
            $display("Passing test : %s", TESTCASE);
        else if (TESTCASE == "testcase_2")
            $display("Passing test : %s", TESTCASE);
        else if ( TESTCASE=="testcase_3" )
            $display("Passing test : %s", TESTCASE);
        else if (TESTCASE== "testcase_4" )
            $display("Passing test : %s", TESTCASE);
        else
            $display("Passing test : %s", TESTCASE);
    end

endmodule