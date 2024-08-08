//HDLRegression:tb
module tb_verilog_testcase #(
        parameter GC_TESTCASE = "DEFAULT",
        parameter GC_DUMMY = "foo"
    );

    initial
    begin
        if (GC_TESTCASE == "testcase_1")
            $display("Passing test : %s (%s)", GC_TESTCASE, GC_DUMMY);
        else if (GC_TESTCASE == "testcase_2")
            $display("Passing test : %s (%s)", GC_TESTCASE, GC_DUMMY);
        else if ( GC_TESTCASE=="testcase_3" )
            $display("Passing test : %s (%s)", GC_TESTCASE, GC_DUMMY);
        else if (GC_TESTCASE== "testcase_4" )
            $display("Passing test : %s (%s)", GC_TESTCASE, GC_DUMMY);
        else
            $display("Failing test : %s (%s)", GC_TESTCASE, GC_DUMMY);
    end

endmodule