--HDLRegression:tb
entity tb_compile_error is
end tb_compile_error;
    
    architecture test of tb_compile_error is
    begin
    
        p_seq : process
        begin
            report "passing testcase";
            -- Finish the simulation
            std.env.stop;
            wait;  -- to stop completely
        end process;
    
        -- create compile error
        wait on error detected;

    end architecture test;