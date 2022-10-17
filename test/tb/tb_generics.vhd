
--HDLRegression:TB
entity tb_generics is
    generic (
        GC_TESTCASE     : string    := "UVVM_TB";
        GC_GENERIC_1    : natural   := 1;
        GC_GENERIC_2    : natural   := 2;
        GC_PATH         : string    := ""
        );
end tb_generics;


architecture test of tb_generics is
begin

    p_seq : process
    begin
        if GC_TESTCASE = "testcase_1" then
            report "PASS: TC1 generic 1 = " & to_string(GC_GENERIC_1) & ", generic 2 = " & to_string(GC_GENERIC_2) & ", path = " & GC_PATH;
        elsif GC_TESTCASE = "testcase_2" then
            report "PASS: TC2 generic 1 = " & to_string(GC_GENERIC_1) & ", generic 2 = " & to_string(GC_GENERIC_2) & ", path = " & GC_PATH;
        else
            report "PASS: DEFAULT generic 1 = " & to_string(GC_GENERIC_1) & ", generic 2 = " & to_string(GC_GENERIC_2) & ", path = " & GC_PATH;
        end if;
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture test;