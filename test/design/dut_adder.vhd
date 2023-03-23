library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity adder is
	Port(
		A   : in  STD_LOGIC_VECTOR(3 downto 0);
		B   : in  STD_LOGIC_VECTOR(3 downto 0);
		SUM : out STD_LOGIC_VECTOR(3 downto 0)
	);
end entity adder;

architecture Behavioral of adder is
begin
	process(A, B)
	begin
		SUM <= A + B;
	end process;
end architecture Behavioral;
