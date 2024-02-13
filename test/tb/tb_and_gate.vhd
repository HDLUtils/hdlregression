library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

--hdlregression:tb
entity tb_and_gate is
end tb_and_gate;

architecture tb of tb_and_gate is
    -- Component declaration for the DUT
    component simple_and_gate
        Port ( A : in STD_LOGIC;
               B : in STD_LOGIC;
               C : out STD_LOGIC);
    end component;

    -- Signals for DUT inputs and output
    signal A : STD_LOGIC := '0';
    signal B : STD_LOGIC := '0';
    signal C : STD_LOGIC;

begin
    -- Instantiate the DUT
    UUT: simple_and_gate Port Map (A => A, B => B, C => C);

    -- Test process
    process
    begin
        -- Apply input combinations and wait for the output
        A <= '0'; B <= '0'; wait for 10 ns;
        assert (C = '0') report "Test failed for A=0, B=0" severity error;

        A <= '0'; B <= '1'; wait for 10 ns;
        assert (C = '0') report "Test failed for A=0, B=1" severity error;

        A <= '1'; B <= '0'; wait for 10 ns;
        assert (C = '0') report "Test failed for A=1, B=0" severity error;

        A <= '1'; B <= '1'; wait for 10 ns;
        assert (C = '1') report "Test failed for A=1, B=1" severity error;

        -- Complete the simulation
        wait;
    end process;

end tb;
