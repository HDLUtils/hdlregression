library ieee;
use ieee.std_logic_1164.all;

--HDLRegression:TB
entity tb_dut is
    generic (
        GC_TESTCASE : string    := "UVVM_TB"
    );
end entity tb_dut;

architecture behavior of tb_dut is
    signal a, b : std_logic_vector(3 downto 0) := (others => '0');
begin
    -- Instantiate the DUT
    uut: entity work.dut
        port map (
            a => a,
            b => b
        );

    -- Test process
    process
    begin
        if GC_TESTCASE = "TC_1" then
            a <= "0001";
            wait for 10 ns;
            assert (b = "0001")
                report "Assertion failed: b is not equal to 0001"
                severity error;
            report "TC done";

        elsif GC_TESTCASE = "TC_2" then
            a <= "0010";
            wait for 10 ns;
            assert (b = "0010")
                report "Assertion failed: b is not equal to 0010"
                severity error;
            report "TC done";
        end if;

        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;
end behavior;
