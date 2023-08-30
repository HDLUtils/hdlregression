use work.rec_c.all;

--HDLRegression:TB
entity rec_b is
end rec_b;

architecture rec_b_arch of rec_b is

begin

    p_seq : process
    begin
        report "testcase done";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture rec_b_arch;