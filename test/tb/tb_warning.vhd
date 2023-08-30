library ieee;
use ieee.std_logic_1164.all;

--hdlregression:tb
entity tb_warning is
end entity;

architecture Behavioral of tb_warning is

  signal foo_1 : std_logic_vector(3 downto 0);
  signal foo_2 : std_logic_vector(2 downto 0);

begin
  process
  begin
    report "This is a warning message." severity warning;
    wait;
  end process;
end architecture;
