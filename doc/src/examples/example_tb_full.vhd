library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

-- Include when using VVC:
-- library uvvm_vvc_framework;
-- use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

--hdlregression:tb
entity tb_example is
  generic (
    GC_TESTCASE : string := "UVVM"
    );
end entity tb_example;

architecture func of tb_example is

  constant C_SCOPE      : string  := C_TB_SCOPE_DEFAULT;
  constant C_CLK_PERIOD : time := 10 ns;

begin

  -----------------------------------------------------------------------------
  -- Instantiate test harness
  -----------------------------------------------------------------------------
  -- i_test_harness : entity work.test_harness;


  ------------------------------------------------
  -- PROCESS: p_main
  ------------------------------------------------
  p_main: process

  begin
    -----------------------------------------------------------------------------
    -- Wait for UVVM to finish initialization
    -----------------------------------------------------------------------------
    -- await_uvvm_initialization(VOID);

    -----------------------------------------------------------------------------
    -- Set UVVM verbosity level
    -----------------------------------------------------------------------------
    -- enable_log_msg(ALL_MESSAGES);
    disable_log_msg(ALL_MESSAGES);
    enable_log_msg(ID_SEQUENCER);
    enable_log_msg(ID_LOG_HDR);

    -----------------------------------------------------------------------------
    -- Test sequence
    -----------------------------------------------------------------------------
    log(ID_SEQUENCER, "Running testcase: " & GC_TESTCASE, C_SCOPE);

    if GC_TESTCASE = "check_reset_defaults" then

      -- reset checks

    elsif GC_TESTCASE = "test_dut_write" then

      -- write checks

    elsif GC_TESTCASE = "test_dut_read" then

      -- read checks

    end if;

    -----------------------------------------------------------------------------
    -- Ending the simulation
    -----------------------------------------------------------------------------
    wait for 1000 ns;             -- to allow some time for completion
    report_alert_counters(FINAL); -- Report final counters and print conclusion for simulation (Success/Fail)
    log(ID_LOG_HDR, "SIMULATION COMPLETED", C_SCOPE);

    -- Finish the simulation
    std.env.stop;
    wait;  -- to stop completely
  end process p_main;

end func;