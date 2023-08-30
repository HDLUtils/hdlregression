use work.rec_a.all;

--HDLRegression:TB
entity rec_c is
end rec_c;

architecture rec_c_arch of rec_c is

begin

    p_seq : process
    begin
        report "testcase done";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture rec_c_arch;