
--HDLRegression:TB
entity tb_testcase is
    generic (
        GC_TESTCASE : string    := "UVVM_TB"
        );
end tb_testcase;


architecture testcase_arch of tb_testcase is
begin

    p_seq : process
    begin

        if GC_TESTCASE = "testcase_1" then
            report "testcase_arch: testcase 1";
        elsif (GC_TESTCASE = "testcase_2") then
            report "testcase_arch: testcase 2";
        elsif ( GC_TESTCASE = "testcase_3" ) then
            report "testcase_arch: testcase 3";
        else
            report "testcase_arch: testcase unknown : " & GC_TESTCASE;
        end if;
        
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture testcase_arch;