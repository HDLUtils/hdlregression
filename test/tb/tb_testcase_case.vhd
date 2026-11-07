
--HDLRegression:TB
entity tb_case_tc is
    generic (
        GC_TESTCASE : string    := "UVVM_TB___"
        );
end tb_case_tc;


architecture tc_arch of tb_case_tc is
begin

    p_seq : process
    begin
        case GC_TESTCASE is
          when "testcase_1" =>
            report "testcase_arch: testcase 1";
          when "testcase_2" =>report "testcase_arch: testcase 2";
          when "testcase_3"=>report "testcase_arch: testcase 3";
          when "testcase_4"=> 
            report "testcase_arch: testcase 4";
          when "testcase_5"=> 
            report"testcase_arch: testcase 5";
          when"testcase_6" => 
            report "testcase_arch: testcase 6" ;
          when "7_testcase" =>
            report "testcase_arch: testcase 7" ;

            when others =>
            report "testcase_arch: testcase unknown : " & GC_TESTCASE;
        end case;
        
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture tc_arch;