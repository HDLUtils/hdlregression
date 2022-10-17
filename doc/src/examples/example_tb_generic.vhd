--hdlregression:tb
entity tb_top is
    generic (
        GC_TESTCASE : string := "read_test"
    );    
end tb_top;

architecture test of simple_tb is
    constant C_SCOPE : string := "SIMPLE_TB"; 
  begin
    p_main : process  
    begin
        if GC_TESTCASE = "read_test" then
            -- read tests
        elsif GC_TESTCASE = "write_test" then
            -- write tests
        else
            report "Unknown test " & GC_TESTCASE;
        end if;
    -- Finish the simulation
    std.env.stop;
    wait;  -- to stop completely        
    end process;
end;