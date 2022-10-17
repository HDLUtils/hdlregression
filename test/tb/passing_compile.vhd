library IEEE;
use IEEE.std_logic_1164.all;

--HDLRegression:tb
entity passing_compile_tb is
end passing_compile_tb;

architecture passing_compile_arch of passing_compile_tb is
begin

    p_seq : process
    begin
        report "passing compilation";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture passing_compile_arch;
