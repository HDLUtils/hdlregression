use work.rec_b.all;

--HDLRegression:TB
entity rec_a is
end rec_a;

architecture rec_a_arch of rec_a is

begin

    p_seq : process
    begin
        report "testcase done";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture rec_a_arch;