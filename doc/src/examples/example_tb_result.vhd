
p_seq : process
    variable v_check_ok : boolean := false;
begin
    -- testcase checks, e.g.
    -- v_check_ok := check_value(v_act_data, v_exp_data, error, "checking receive data", C_SCOPE);
    
    if v_check_ok = true then
        report "testcase passed";
    end if;

    -- Finish the simulation
    std.env.stop;
    wait;  -- to stop completely
end process;