--HDLRegression:tb
entity tb_new_passing is
    end tb_new_passing;
    
    architecture test of tb_new_passing is
    begin
    
        p_seq : process
        begin
            report "passing testcase";
            -- Finish the simulation
            std.env.stop;
            wait;  -- to stop completely
        end process;
    
    end architecture test;