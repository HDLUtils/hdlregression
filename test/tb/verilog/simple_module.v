module simple_module (input     up_down,
							    clk,
							    rstn,
            output reg [2:0] 	out);

	always @ (posedge clk)
		if (!rstn)
			out <= 0;
		else begin
			if (up_down)
				out <= out + 1;
			else
				out <= out - 1;
		end
endmodule