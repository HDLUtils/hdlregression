library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.finish;

library uvvm_util;
context uvvm_util.uvvm_util_context;

-------------------------------------------------------------------------------

--HDLRegression:tb
entity simple_tb is
  generic (
    GC_TESTCASE : string := "UVVM";
    GC_1        : natural := 1
    );
end entity simple_tb;

-------------------------------------------------------------------------------

architecture test_arch of simple_tb is
  constant C_SCOPE                : string := "SIMPLE_TB";

begin

  ------------------------------------------------
  -- PROCESS: p_main
  ------------------------------------------------
  p_main : process
  
  begin

    ---- To avoid that log files from different test cases (run in separate
    ---- simulations) overwrite each other.
    --set_log_file_name(GC_TESTCASE & "_Log.txt");
    --set_alert_file_name(GC_TESTCASE & "_Alert.txt");

    -- Set all appropriate log settings
    --disable_log_msg(ALL_MESSAGES);

    check_value(True, TB_WARNING, "activating checking", C_SCOPE);

    report "passing testcase";
 
    -----------------------------------------------------------------------------
    -- Ending the simulation
    -----------------------------------------------------------------------------
    report_alert_counters(FINAL);
    --report_alert_counters(INTERMEDIATE);                                          
    finish;
    --std.env.stop;
    --wait;
    end process p_main;

end architecture test_arch;
