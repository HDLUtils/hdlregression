// half_adder.v

module half_adder
(
    input wire a, b,
    output wire sum, carry
);

assign sum = a ^ b;
assign carry = a & b;

endmodule