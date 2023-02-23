//-----------------------------------------------------
// Design Name : up_counter
// File Name   : up_counter.sv
// Function    : Up counter
// Coder      : Deepak
//-----------------------------------------------------
module up_counter    (
output reg [7:0] out     ,  // Output of the counter
input  wire      enable  ,  // enable for counter
input  wire      clk     ,  // clock Input
input  wire      reset      // reset Input
);
//-------------Code Starts Here-------
always_ff @(posedge clk)
if (reset) begin
  out <= 8'b0 ;
end else if (enable) begin
  out ++;
end

endmodule 