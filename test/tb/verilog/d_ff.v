module d_ff (clk, resetn, q, d);

  input clk;
  input resetn;
  input d;
  output q;

  reg q;

  always @ (posedge clk)
    if (! resetn)
      q <= 0;
    else
      q <= d;

endmodule