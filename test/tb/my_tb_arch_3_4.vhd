architecture arch_3 of my_tb_arch is
begin

    p_seq : process
    begin
        report "arch_3 : sim done";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture arch_3;


architecture arch_4 of my_tb_arch is
begin

    p_seq : process
    begin
        report "arch_4 : sim done";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture arch_4;