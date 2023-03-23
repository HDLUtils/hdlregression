
library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

--HDLRegression:TB
entity demo_tb is
    generic (
        GC_TESTCASE     : string    := "UVVM_TB";
        GC_1    : natural   := 1;
        GC_2    : natural   := 2;
        GC_PATH         : string    := ""
        );
end demo_tb;


architecture demo_arch of demo_tb is

    constant C_SCOPE : string := "DEMO_SEQ";

begin

    p_seq : process
    begin
        if GC_TESTCASE = "testcase_1" then
            report "PASS: TC1 generic 1 = " & to_string(GC_1) & ", generic 2 = " & to_string(GC_2) & ", path = " & GC_PATH;
        elsif GC_TESTCASE = "testcase_2" then
            report "PASS: TC2 generic 1 = " & to_string(GC_1) & ", generic 2 = " & to_string(GC_2) & ", path = " & GC_PATH;
        elsif GC_TESTCASE = "failing_test" then
            check_value(GC_1 = GC_2, ERROR, "check: " & to_string(GC_1) & " = " & to_string(GC_2) & ".", C_SCOPE);
        else
            report "PASS: DEFAULT generic 1 = " & to_string(GC_1) & ", generic 2 = " & to_string(GC_2) & ", path = " & GC_PATH;
        end if;


        -----------------------------------------------------------------------------
        -- Ending the simulation
        -----------------------------------------------------------------------------
        wait for 1000 ns;               -- to allow some time for completion
        report_alert_counters(FINAL);   -- Report final counters and print conclusion for simulation (Success/Fail)
        log(ID_LOG_HDR, "SIMULATION COMPLETED", C_SCOPE);
        -- Finish the simulation
        std.env.stop;
        wait;                           -- to stop completely
    end process;

end architecture demo_arch;