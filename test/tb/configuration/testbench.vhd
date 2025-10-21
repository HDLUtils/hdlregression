library IEEE;
use IEEE.std_logic_1164.all;

-- Test bench for Sigasi Tutorial Project.
--HDLRegression:tb
entity testbench is
end entity testbench;

architecture struct of testbench is
	component dut_dev
		port(a : in string;
			 b : in string;
			 c : in string);
	end component dut_dev;

	signal a : string(1 to 1) := "A";
	signal b : string(1 to 1) := "B";
	signal c : string(1 to 1) := "C";
	
begin

	dut_inst : component dut_dev
		port map(a => a,
			     b => b,
			     c => c);

end architecture struct;
