
--HDLRegression:TB
entity tb_rand is
    generic (
        GC_TESTCASE : string    := "UVVM_TB";
        GC_RAND_1   : natural   := 5;
        GC_RAND_2   : natural   := 25
        );
end tb_rand;


architecture rand_arch of tb_rand is
begin

    p_seq : process
    begin
        if GC_TESTCASE = "testcase_1" then
            report "TC1: random seed1 = " & to_string(GC_RAND_1) & ", seed2 = " & to_string(GC_RAND_2) & ".";
        elsif GC_TESTCASE = "testcase_2" then
            report "TC2: random seed1 = " & to_string(GC_RAND_1) & ", seed2 = " & to_string(GC_RAND_2) & ".";
        else
            report "random seed1 = " & to_string(GC_RAND_1) & ", seed2 = " & to_string(GC_RAND_2) & ".";
        end if;
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture rand_arch;