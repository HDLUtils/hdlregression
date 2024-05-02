library uvvm_util;
context uvvm_util.uvvm_util_context;

--HDLRegression:TB

entity tb_failing_after_report is
end entity;

architecture failing_arch of tb_failing_after_report is

  constant C_SCOPE : string := "TB_SEQ";

begin

  p_seq: process
  begin
    report_alert_counters(FINAL);

    wait for 0 ns;
    alert(ERROR, "trigger alert", C_SCOPE);
    std.env.stop;
    wait;
  end process;

end architecture;
