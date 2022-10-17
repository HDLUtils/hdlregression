--HDLRegression:tb
entity tb_failing is
end tb_failing;

architecture test of tb_failing is
begin

    p_seq : process
    begin
        report "failing testcase";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture test;