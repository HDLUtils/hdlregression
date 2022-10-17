library IEEE;
use IEEE.std_logic_1164.all;

entity dut_dev is
	port(
		a : in string;
		b : in string;
		c : in string
	);
end entity dut_dev;

architecture rtl of dut_dev is

begin
	process is
	begin
		report "this is dut_dev(rtl)"; 
		report "port a:" & a;
		report "port b:" & b;
		report "port c:" & c;
		wait;
	end process;
end architecture rtl;
