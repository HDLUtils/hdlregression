-- Simple DUT with an input and output
library ieee;
use ieee.std_logic_1164.all;

entity dut is
    port(
        a : in std_logic_vector(3 downto 0);
        b : out std_logic_vector(3 downto 0)
    );
end entity;

architecture behavior of dut is
begin
    b <= a;
end behavior;
