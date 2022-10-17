--HDLRegression:TB
entity my_tb_io is
end my_tb_io;


architecture io_file_arch of my_tb_io is
begin

    p_seq : process
    /*
    This process will output the input and output
    file name */
    
    begin
        report "input file = my_input_file, output file = my_output_file.";
        -- Finish the simulation
        std.env.stop;
        wait;  -- to stop completely
    end process;

end architecture io_file_arch;