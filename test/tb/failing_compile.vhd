library IEEE;
use IEEE.std_logic_1164.all;

--HDLRegression:tb
entity failing_compile is
end failing_compile;

architecture failing_compile_arch of failing_compile is
begin

    p_seq : process
    begin
        -- trigger a compilation error
        check_();
        
        report "failing compilation";
        
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture failing_compile_arch;
