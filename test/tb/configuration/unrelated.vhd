library IEEE;
use IEEE.std_logic_1164.all;

entity unrelated_dev is
	port(
		port1 : in string;
		port2 : in string;
		port3 : in string;
		port4 : in string
	);
end entity unrelated_dev;

architecture rtl of unrelated_dev is

begin
	process is
	begin
		report "this is unrelated_dev(rtl)"; 
		report "port 1:" & port1;
		report "port 2:" & port2;
		report "port 3:" & port3;
		report "port 4:" & port4;
		wait;
	end process;
end architecture rtl;
