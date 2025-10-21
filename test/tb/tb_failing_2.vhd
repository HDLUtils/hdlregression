--HDLRegression:tb
entity tb_failing_2 is
    end tb_failing_2;
    
    architecture test of tb_failing_2 is
    begin
    
        p_seq : process
        begin
            report "failing testcase";
            -- Finish the simulation
            std.env.stop;
            wait;  -- to stop completely
        end process;
    
    end architecture test;