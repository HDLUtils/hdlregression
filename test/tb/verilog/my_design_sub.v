module mydesignsub ( input  x, y, z,     // x is at position 1, y at 2, x at 3 and
                     output o);          // o is at position 4

endmodule

module tb_top;
	wire [1:0]  a;
	wire        b, c;

	mydesignsub d0  (a[0], b, a[1], c);  // a[0] is at position 1 so it is automatically connected to x
	                                  // b is at position 2 so it is automatically connected to y
	                                  // a[1] is at position 3 so it is connected to z
	                                  // c is at position 4, and hence connection is with o
endmodule