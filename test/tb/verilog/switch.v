// code from http://testbench.in/VS_02_RTL.html

module fifo (clk, 
reset, 
write_enb, 
read, 
data_in, 
data_out, 
empty, 
full); 
input clk; 
input reset; 
input write_enb; 
input read; 
input [7:0] data_in; 
output [7:0] data_out; 
output empty; 
output full; 
wire clk; 
wire write_enb; 
wire read; 
wire [7:0] data_in; 
reg [7:0] data_out; 
wire empty; 
wire full; 
reg [7:0] ram[0:25]; 
reg tmp_empty; 
reg tmp_full; 
integer write_ptr; 
integer read_ptr; 
always@(negedge reset) 
begin 
data_out = 8'b0000_0000; 
tmp_empty = 1'b1; 
tmp_full = 1'b0; 
write_ptr = 0; 
read_ptr = 0; 
end 

assign empty = tmp_empty; 
assign full = tmp_full; 
always @(posedge clk) begin 
if ((write_enb == 1'b1) && (tmp_full == 1'b0)) begin 
ram[write_ptr] = data_in; 
tmp_empty <= 1'b0; 
write_ptr = (write_ptr + 1) % 16; 
if ( read_ptr == write_ptr ) begin 
tmp_full <= 1'b1; 
end 
end 

if ((read == 1'b1) && (tmp_empty == 1'b0)) begin 
data_out <= ram[read_ptr]; 
tmp_full <= 1'b0; 
read_ptr = (read_ptr + 1) % 16; 
if ( read_ptr == write_ptr ) begin 
tmp_empty <= 1'b1; 
end 
end 
end 
endmodule //fifo 

module port_fsm (clk, 
reset, 
write_enb, 
ffee, 
hold, 
data_status, 
data_in, 
data_out, 
mem0, 
mem1, 
mem2, 
mem3, 
addr); 
input clk; 
input reset; 
input [7:0] mem0; 
input [7:0] mem1; 
input [7:0] mem2; 
input [7:0] mem3; 
output[3:0] write_enb; 
input ffee; 
input hold; 
input data_status; 
input[7:0] data_in; 
output[7:0] data_out; 
output [7:0] addr; 
reg [7:0] data_out; 
reg [7:0] addr; 
reg [3:0] write_enb_r; 
reg fsm_write_enb; 
reg [3:0] state_r; 
reg [3:0] state; 
reg [7:0] parity; 
reg [7:0] parity_delayed; 
reg sus_data_in,error; 

parameter ADDR_WAIT = 4'b0000; 
parameter DATA_LOAD = 4'b0001; 
parameter PARITY_LOAD = 4'b0010; 
parameter HOLD_STATE = 4'b0011; 
parameter BUSY_STATE = 4'b0100; 

always@(negedge reset) 
begin 
error = 1'b0; 
data_out = 8'b0000_0000; 
addr = 8'b00000000; 
write_enb_r = 3'b000; 
fsm_write_enb = 1'b0; 
state_r = 4'b0000; 
state = 4'b0000; 
parity = 8'b0000_0000; 
parity_delayed = 8'b0000_0000; 
sus_data_in = 1'b0; 
end 
assign busy = sus_data_in; 
always @(data_status) begin : addr_mux 
if (data_status == 1'b1) begin 
case (data_in) 
mem0 : begin 
write_enb_r[0] = 1'b1; 
write_enb_r[1] = 1'b0; 
write_enb_r[2] = 1'b0; 
write_enb_r[3] = 1'b0; 
end 
mem1 : begin 
write_enb_r[0] = 1'b0; 
write_enb_r[1] = 1'b1; 
write_enb_r[2] = 1'b0; 
write_enb_r[3] = 1'b0; 
end 
mem2 : begin 
write_enb_r[0] = 1'b0; 
write_enb_r[1] = 1'b0; 
write_enb_r[2] = 1'b1; 
write_enb_r[3] = 1'b0; 
end 

mem3 : begin 
write_enb_r[0] = 1'b0; 
write_enb_r[1] = 1'b0; 
write_enb_r[2] = 1'b0; 
write_enb_r[3] = 1'b1; 
end 
default :write_enb_r = 3'b000; 
endcase 
// $display(" data_inii %d ,mem0 %d ,mem1 %d ,mem2 %d mem3",data_in,mem0,mem1,mem2,mem3); 
end //if 
end //addr_mux; 
always @(posedge clk) begin : fsm_state 
state_r <= state; 
end //fsm_state; 

always @(state_r or data_status or ffee or hold or data_in) 
begin : fsm_core 
state = state_r; //Default state assignment 
case (state_r) 
ADDR_WAIT : begin 
if ((data_status == 1'b1) && 
((mem0 == data_in)||(mem1 == data_in)||(mem3 == data_in) ||(mem2 == data_in))) begin 
if (ffee == 1'b1) begin 
state = DATA_LOAD; 
end 
else begin 
state = BUSY_STATE; 
end //if 
end //if; 
sus_data_in = !ffee; 
if ((data_status == 1'b1) && 
((mem0 == data_in)||(mem1 == data_in)||(mem3 == data_in) ||(mem2 == data_in)) && 
(ffee == 1'b1)) begin 
addr = data_in; 
data_out = data_in; 
fsm_write_enb = 1'b1; 

end 
else begin 
fsm_write_enb = 1'b0; 
end //if 
end // of case ADDR_WAIT 
PARITY_LOAD : begin 
state = ADDR_WAIT; 
data_out = data_in; 
fsm_write_enb = 1'b0; 
end // of case PARITY_LOAD 
DATA_LOAD : begin 
if ((data_status == 1'b1) && 
(hold == 1'b0)) begin 
state = DATA_LOAD; 
end 
else if ((data_status == 1'b0) && 
(hold == 1'b0)) begin 
state = PARITY_LOAD; 
end 
else begin 
state = HOLD_STATE; 
end //if 
sus_data_in = 1'b0; 
if ((data_status == 1'b1) && 
(hold == 1'b0)) begin 
data_out = data_in; 
fsm_write_enb = 1'b1; 
end 
else if ((data_status == 1'b0) && 
(hold == 1'b0)) begin 
data_out = data_in; 
fsm_write_enb = 1'b1; 
end 
else begin 
fsm_write_enb = 1'b0; 
end //if 
end //end of case DATA_LOAD 
HOLD_STATE : begin 
if (hold == 1'b1) begin 
state = HOLD_STATE; 
end 
else if ((hold == 1'b0) && (data_status == 1'b0)) begin 
state = PARITY_LOAD; 
end 
else begin 
state = DATA_LOAD; 
end //if 
if (hold == 1'b1) begin 
sus_data_in = 1'b1; 
fsm_write_enb = 1'b0; 
end 
else begin 
fsm_write_enb = 1'b1; 
data_out = data_in; 
end //if 
end //end of case HOLD_STATE 
BUSY_STATE : begin 
if (ffee == 1'b0) begin 
state = BUSY_STATE; 
end 
else begin 
state = DATA_LOAD; 
end //if 
if (ffee == 1'b0) begin 
sus_data_in = 1'b1; 
end 
else begin 
addr = data_in; // hans 
data_out = data_in; 
fsm_write_enb = 1'b1; 
end //if 
end //end of case BUSY_STATE 
endcase 
end //fsm_core 

assign write_enb[0] = write_enb_r[0] & fsm_write_enb; 
assign write_enb[1] = write_enb_r[1] & fsm_write_enb; 
assign write_enb[2] = write_enb_r[2] & fsm_write_enb; 
assign write_enb[3] = write_enb_r[3] & fsm_write_enb; 

endmodule //port_fsm 
module switch (clk, 
reset, 
data_status, 
data, 
port0, 
port1, 
port2, 
port3, 
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
input clk; 
input reset; 
input data_status; 
input [7:0] data; 
input mem_en; 
input mem_rd_wr; 
input [1:0] mem_add; 
input [7:0] mem_data; 
output [7:0] port0; 
output [7:0] port1; 
output [7:0] port2; 
output [7:0] port3; 
output ready_0; 
output ready_1; 
output ready_2; 
output ready_3; 
input read_0; 
input read_1; 
input read_2; 
input read_3; 
wire [7:0] data_out_0; 
wire [7:0] data_out_1; 
wire [7:0] data_out_2; 
wire [7:0] data_out_3; 
wire ll0; 
wire ll1; 
wire ll2; 
wire ll3; 
wire empty_0; 
wire empty_1; 
wire empty_2; 
wire empty_3; 
wire ffee; 
wire ffee0; 
wire ffee1; 
wire ffee2; 
wire ffee3; 
wire ld0; 
wire ld1; 
wire ld2; 
wire ld3; 
wire hold; 
wire [3:0] write_enb; 
wire [7:0] data_out_fsm; 
wire [7:0] addr; 

reg [7:0]mem[3:0]; 
wire reset; 
fifo queue_0 (.clk (clk), 
.reset (reset), 
.write_enb (write_enb[0]), 
.read (read_0), 
.data_in (data_out_fsm), 
.data_out (data_out_0), 
.empty (empty_0), 
.full (ll0)); 

fifo queue_1 (.clk (clk), 
.reset (reset), 
.write_enb (write_enb[1]), 
.read (read_1), 
.data_in (data_out_fsm), 
.data_out (data_out_1), 
.empty (empty_1), 
.full (ll1)); 

fifo queue_2 (.clk (clk), 
.reset (reset), 
.write_enb (write_enb[2]), 
.read (read_2), 
.data_in (data_out_fsm), 
.data_out (data_out_2), 
.empty (empty_2), 
.full (ll2)); 

fifo queue_3 (.clk (clk), 
.reset (reset), 
.write_enb (write_enb[3]), 
.read (read_3), 
.data_in (data_out_fsm), 
.data_out (data_out_3), 
.empty (empty_3), 
.full (ll3)); 



port_fsm in_port (.clk (clk), 
.reset (reset), 
.write_enb (write_enb), 
.ffee (ffee), 
.hold (hold), 
.data_status (data_status), 
.data_in (data), 
.data_out (data_out_fsm), 
.mem0 (mem[0]), 
.mem1 (mem[1]), 
.mem2 (mem[2]), 
.mem3 (mem[3]), 
.addr (addr)); 
assign port0 = data_out_0; //make note assignment only for 
//consistency with vlog env 
assign port1 = data_out_1; 
assign port2 = data_out_2; 
assign port3 = data_out_3; 

assign ready_0 = ~empty_0; 
assign ready_1 = ~empty_1; 
assign ready_2 = ~empty_2; 
assign ready_3 = ~empty_3; 

assign ffee0 = (empty_0 | ( addr != mem[0])); 
assign ffee1 = (empty_1 | ( addr != mem[1])); 
assign ffee2 = (empty_2 | ( addr != mem[2])); 
assign ffee3 = (empty_3 | ( addr != mem[3])); 

assign ffee = ffee0 & ffee1 & ffee2 & ffee3; 

assign ld0 = (ll0 & (addr == mem[0])); 
assign ld1 = (ll1 & (addr == mem[1])); 
assign ld2 = (ll2 & (addr == mem[2])); 
assign ld3 = (ll3 & (addr == mem[3])); 

assign hold = ld0 | ld1 | ld2 | ld3; 

always@(posedge clk) 
begin 

if(mem_en) 
if(mem_rd_wr) 
begin 
mem[mem_add]=mem_data; 
///$display("%d %d %d %d %d",mem_add,mem[0],mem[1],mem[2],mem[3]); 
end 
end 
endmodule //router 