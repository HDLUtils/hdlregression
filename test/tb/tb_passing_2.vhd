--HDLRegression:tb
entity tb_simple_passing is
end entity tb_simple_passing;

-------------------------------------------------------------------------------

architecture test_arch of tb_simple_passing is
begin

    p_seq : process
    begin
        report "passing testcase";
        -- Finish the simulation
        std.env.stop;
        wait;                           -- to stop completely
    end process;

end architecture test_arch;
