library IEEE;
use IEEE.std_logic_1164.all;

--HDLRegression:TB
entity my_tb_rand is
    generic (
        GC_TESTCASE : string    := "UVVM_TB";
        GC_RAND_1   : natural   := 5;
        GC_RAND_2   : natural   := 25
        );
end my_tb_rand;

architecture rand_arch of my_tb_rand is
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


-- No library for this entity / architecture
entity my_tb_rand_2 is
    generic (
        GC_TESTCASE : string    := "UVVM_TB";
        GC_RAND_1   : natural   := 5;
        GC_RAND_2   : natural   := 25
        );
end my_tb_rand_2;


architecture rand_arch_2 of my_tb_rand_2 is
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

end architecture rand_arch_2;