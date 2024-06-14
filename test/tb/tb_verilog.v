//HDLRegression:tb
module tb_verilog_testcase #(
        parameter GC_TESTCASE = "DEFAULT"
    );

    initial
    begin
        if (GC_TESTCASE == "testcase_1")
            $display("Passing test : %s", GC_TESTCASE);
        else if (GC_TESTCASE == "testcase_2")
            $display("Passing test : %s", GC_TESTCASE);
        else if ( GC_TESTCASE=="testcase_3" )
            $display("Passing test : %s", GC_TESTCASE);
        else if (GC_TESTCASE== "testcase_4" )
            $display("Passing test : %s", GC_TESTCASE);
        else
            $display("Passing test : %s", GC_TESTCASE);
    end

endmodule