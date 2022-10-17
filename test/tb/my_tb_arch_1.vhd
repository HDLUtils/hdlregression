architecture arch_1 of my_tb_arch is
begin

    p_seq : process
    begin
        report "arch_1";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture arch_1;