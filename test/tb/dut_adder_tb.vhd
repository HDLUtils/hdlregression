library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use std.env.finish;

--hdlregression:tb
entity adder_tb is
end entity adder_tb;

architecture sim of adder_tb is
	signal A, B, SUM : STD_LOGIC_VECTOR(3 downto 0);

	component adder
		Port(
			A   : in  STD_LOGIC_VECTOR(3 downto 0);
			B   : in  STD_LOGIC_VECTOR(3 downto 0);
			SUM : out STD_LOGIC_VECTOR(3 downto 0)
		);
	end component;

begin

	i_adder_inst : adder
		Port map(
			A   => A,
			B   => B,
			SUM => SUM
		);

	stimulus_process : process
	begin
		-- Test case 1: A = 4, B = 3
		A <= "0100";
		B <= "0011";
		wait for 10 ns;

		-- Test case 2: A = 15, B = 1
		A <= "1111";
		B <= "0001";
		wait for 10 ns;

		-- Test case 3: A = 0, B = 0
		A <= "0000";
		B <= "0000";
		wait for 10 ns;

		-- Test case 4: A = 7, B = 9
		A <= "0111";
		B <= "1001";
		wait for 10 ns;

		report "passing testcase";
		finish;
	end process stimulus_process;

end architecture sim;
