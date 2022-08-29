// code from http://testbench.in/VS_03_TOP.html

module top(); 
reg clock; 
wire packet_valid; 
wire [7:0] data; 
wire [7:0] data_0; 
wire [7:0] data_1; 
wire [7:0] data_2; 
wire [7:0] data_3; 
wire ready_0; 
wire ready_1; 
wire ready_2; 
wire ready_3; 
wire read_0; 
wire read_1; 
wire read_2; 
wire read_3; 

reg reset; 
reg mem_en; 
reg mem_rd_wr; 
reg [7:0] mem_data; 
reg [1:0] mem_add; 
reg [7:0] mem[3:0]; 

// take istance of testbench 
sw_tb tb (clock, 
packet_valid, 
data, 
data_0, 
data_1, 
data_2, 
data_3, 
ready_0, 
ready_1, 
ready_2, 
ready_3, 
read_0, 
read_1, 
read_2, 
read_3); 

// take instance dut 
switch dut (clock, 
reset, 
packet_valid, 
data, 
data_0, 
data_1, 
data_2, 
data_3, 
ready_0, 
ready_1, 
ready_2, 
ready_3, 
read_0, 
read_1, 
read_2, 
read_3, 
mem_en, 
mem_rd_wr, 
mem_add, 
mem_data); 


//Clock generator 
initial 
clock = 0; 
always 
begin 
#5 clock = !clock; 
end 

// Do reset and configure the dut port address 
initial begin 
$dumpon; 
mem[0]=$random; 
mem[1]=$random; 
mem[2]=$random; 
mem[3]=$random; 
mem_en = 0; 
@(posedge clock); 
#2 reset = 1; 
@(posedge clock); 
#2 reset =0; 
mem_en = 1; 
@(negedge clock); 
mem_rd_wr = 1; 
mem_add = 0; 
mem_data = mem[0]; 
@(negedge clock); 
mem_rd_wr = 1; 
mem_add = 1; 
mem_data = mem[1]; 
@(negedge clock); 
mem_rd_wr = 1; 
mem_add = 2; 
mem_data = mem[2]; 
@(negedge clock); 
mem_rd_wr = 1; 
mem_add = 3; 
mem_data = mem[3]; 
@(negedge clock); 
mem_en=0; 
mem_rd_wr = 0; 
mem_add = 0; 
mem_data = 0; 
end 



endmodule //top 