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
        case GC_TESTCASE is
          when "read_test" =>
            -- read tests
        when "write_test" =>
            -- write tests
        when others =>
            report "Unknown test " & GC_TESTCASE;
        end case;
    -- Finish the simulation
    std.env.stop;
    wait;  -- to stop completely        
    end process;
end;