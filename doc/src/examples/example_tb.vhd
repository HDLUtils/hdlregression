library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

library uvvm_util;
context uvvm_util.uvvm_util_context;

library uvvm_vvc_framework;
use uvvm_vvc_framework.ti_vvc_framework_support_pkg.all;

library bitvis_vip_sbi;
use bitvis_vip_sbi.vvc_methods_pkg.all;
use bitvis_vip_sbi.td_vvc_framework_common_methods_pkg.all;

library bitvis_vip_clock_generator;
context bitvis_vip_clock_generator.vvc_context;

library bitvis_vip_uart;
use bitvis_vip_uart.vvc_methods_pkg.all;
use bitvis_vip_uart.td_vvc_framework_common_methods_pkg.all;

--hdlregression:tb
entity uart_tb is
  generic (
    GC_TESTCASE : string := "UVVM"
    );
end entity;

architecture func of uart_tb is

  constant C_SCOPE : string := C_TB_SCOPE_DEFAULT;
  -- Clock and bit period settings
  constant C_CLK_PERIOD : time := 10 ns;
  constant C_BIT_PERIOD : time := 16 * C_CLK_PERIOD;
  -- Time for one UART transmission to complete
  constant C_TIME_OF_ONE_UART_TX : time := 11*C_BIT_PERIOD;
  -- Predefined SBI addresses
  constant C_ADDR_RX_DATA       : unsigned(3 downto 0) := x"0";
  constant C_ADDR_RX_DATA_VALID : unsigned(3 downto 0) := x"1";
  constant C_ADDR_TX_DATA       : unsigned(3 downto 0) := x"2";
  constant C_ADDR_TX_READY      : unsigned(3 downto 0) := x"3";

begin

  -----------------------------------------------------------------------------
  -- Instantiate test harness, containing DUT and Executors
  -----------------------------------------------------------------------------
  i_test_harness : entity work.uart_vvc_demo_th;


  ------------------------------------------------
  -- PROCESS: p_main
  ------------------------------------------------
  p_main : process
  begin
    set_log_file_name(GC_TESTCASE & "_Log.txt");
    set_alert_file_name(GC_TESTCASE & "_Alert.txt");

    -- Wait for UVVM to finish initialization
    await_uvvm_initialization(VOID);

    start_clock(CLOCK_GENERATOR_VVCT, 1, "Start clock generator");

    -- Print the configuration to the log
    report_global_ctrl(VOID);
    report_msg_id_panel(VOID);

    disable_log_msg(ALL_MESSAGES);
    enable_log_msg(ID_LOG_HDR);
    enable_log_msg(ID_SEQUENCER);
    enable_log_msg(ID_UVVM_SEND_CMD);

    disable_log_msg(SBI_VVCT, 1, ALL_MESSAGES);
    enable_log_msg(SBI_VVCT, 1, ID_BFM);
    disable_log_msg(UART_VVCT, 1, RX, ALL_MESSAGES);
    enable_log_msg(UART_VVCT, 1, RX, ID_BFM);
    disable_log_msg(UART_VVCT, 1, TX, ALL_MESSAGES);
    enable_log_msg(UART_VVCT, 1, TX, ID_BFM);

    log(ID_LOG_HDR, "Configure UART VVC 1", C_SCOPE);
    ------------------------------------------------------------
    shared_uart_vvc_config(TX, 1).bfm_config.bit_time := C_BIT_PERIOD;
    shared_uart_vvc_config(RX, 1).bfm_config.bit_time := C_BIT_PERIOD;

    log(ID_LOG_HDR, "Starting simulation of TB for UART using VVCs", C_SCOPE);
    ------------------------------------------------------------
    log("Wait 10 clock period for reset to be turned off");
    wait for (10 * C_CLK_PERIOD);       -- for reset to be turned off

    if GC_TESTCASE = "check_register_defaults" then
      log(ID_LOG_HDR, "Check register defaults ", C_SCOPE);
      sbi_check(SBI_VVCT, 1, C_ADDR_RX_DATA, x"00", "RX_DATA default");
      sbi_check(SBI_VVCT, 1, C_ADDR_TX_READY, x"01", "TX_READY default");
      sbi_check(SBI_VVCT, 1, C_ADDR_RX_DATA_VALID, x"00", "RX_DATA_VALID default");
      await_completion(SBI_VVCT, 1, 10 * C_CLK_PERIOD);

    elsif GC_TESTCASE = "check_simple_transmit" then
      log(ID_LOG_HDR, "Check simple transmit", C_SCOPE);
      sbi_write(SBI_VVCT, 1, C_ADDR_TX_DATA, x"55", "TX_DATA");
      uart_expect(UART_VVCT, 1, RX, x"55", "Expecting data on UART RX");
      await_completion(UART_VVCT, 1, RX, 13 * C_BIT_PERIOD);
      wait for 200 ns;

    else
      if GC_TESTCASE /= "ALL" then
        alert(tb_error, "Unsupported test: " & GC_TESTCASE);
      end if;
    end if;

    -----------------------------------------------------------------------------
    -- Ending the simulation
    -----------------------------------------------------------------------------
    wait for 1000 ns;                   -- to allow some time for completion
    report_alert_counters(FINAL);  -- Report final counters and print conclusion for simulation (Success/Fail)
    log(ID_LOG_HDR, "SIMULATION COMPLETED", C_SCOPE);
    -- Finish the simulation
    std.env.stop;
    wait;                               -- to stop completely
  end process p_main;
end func;
