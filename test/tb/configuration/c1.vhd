configuration c1 of testbench is
	for struct
		for dut_inst : dut_dev
			use entity work.dut_dev(rtl);
		end for;
	end for;
end configuration c1;

configuration c2 of testbench is
	for struct
		for dut_inst : dut_dev
			use entity work.unrelated_dev(rtl)
				port map(
					port1 => a,
					port2 => b,
					port3 => c,
					port4 => "unused"
				);
		end for;
	end for;
end configuration c2;

configuration c3 of testbench is
	for struct
		for dut_inst : dut_dev
			use entity work.dut_dev(rtl)
				port map(
					a => b,
					b => c,
					c => a
				);
		end for;
	end for;
end configuration c3;
