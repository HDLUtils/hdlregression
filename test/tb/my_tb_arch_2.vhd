
architecture arch_2 of my_tb_arch is
begin

    p_seq : process
    begin
        report "arch_2 : sim done";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture arch_2;