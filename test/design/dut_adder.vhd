library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.numeric_std.all;

entity adder is
	Port(
		A   : in  std_logic_vector(3 downto 0);
		B   : in  std_logic_vector(3 downto 0);
		SUM : out std_logic_vector(3 downto 0)
	);
end entity adder;

architecture Behavioral of adder is
begin

	sum <= std_logic_vector(unsigned(a) + unsigned(b));

end architecture Behavioral;
