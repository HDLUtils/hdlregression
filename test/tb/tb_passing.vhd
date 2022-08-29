--HDLRegression:tb
entity tb_passing is
    end tb_passing;
    
    architecture test of tb_passing is
    begin
    
        p_seq : process
        begin
            report "passing testcase";
            -- Finish the simulation
            std.env.stop;
            wait;  -- to stop completely
        end process;
    
    end architecture test;