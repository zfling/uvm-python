// 
// -------------------------------------------------------------
//    Copyright 2004-2011 Synopsys, Inc.
//    Copyright 2010 Mentor Graphics Corporation
//    Copyright 2010 Cadence Design Systems, Inc.
//    All Rights Reserved Worldwide
// 
//    Licensed under the Apache License, Version 2.0 (the
//    "License"); you may not use this file except in
//    compliance with the License.  You may obtain a copy of
//    the License at
// 
//        http://www.apache.org/licenses/LICENSE-2.0
// 
//    Unless required by applicable law or agreed to in
//    writing, software distributed under the License is
//    distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
//    CONDITIONS OF ANY KIND, either express or implied.  See
//    the License for the specific language governing
//    permissions and limitations under the License.
// -------------------------------------------------------------
// 

`timescale 1ns/1ns

module slave#(
    parameter int MEM_SIZE = 128,
    parameter int NSOCKETS = 64,
    parameter int ID_REGISTER = {2'b00, 4'h0, 10'h176, 8'h5A, 8'h03}
)
(
   input apb_pclk,
   input bit rst,
   input wire [31:0] apb_paddr,
   input        apb_psel,
   input        apb_penable,
   input        apb_pwrite,
   output [31:0] apb_prdata,
   input [31:0] apb_pwdata
);

reg [31:0] pr_data;
assign apb_prdata = (apb_psel && apb_penable && !apb_pwrite) ? pr_data : 'z;

reg [31:0] DATA;
reg [63:0] SOCKET[NSOCKETS];
reg [31:0] DMA[MEM_SIZE];

always @ (posedge apb_pclk)
  begin
   if (rst) begin
      DATA <= 'h00;
      foreach (SOCKET[i]) begin
         SOCKET[i] <= 64'h0000_0000;
      end
      pr_data <= 32'h0;
   end
   else begin

      // Wait for a SETUP+READ or ENABLE+WRITE cycle
      if (apb_psel == 1'b1 && apb_penable == apb_pwrite) begin
         pr_data <= 32'h0;
         if (apb_pwrite) begin
            casex (apb_paddr)
              16'h0024: DATA <= apb_pwdata;
              16'h1XX0: SOCKET[apb_paddr[11:4]][63:32] <= apb_pwdata; 
              16'h1XX4: SOCKET[apb_paddr[11:4]][31: 0] <= apb_pwdata;
              16'h2XXX: DMA[apb_paddr[11:2]] <= apb_pwdata;
            endcase
         end
         else begin
            casex (apb_paddr)
              16'h0000: pr_data <= ID_REGISTER;
              16'h0024: pr_data <= DATA;
              16'h1XX0: pr_data <= SOCKET[apb_paddr[11:4]][63:32];
              16'h1XX4: pr_data <= SOCKET[apb_paddr[11:4]][31: 0];
              16'h2XXX: pr_data <= DMA[apb_paddr[11:2]];
            endcase
         end
      end
   end
end

`ifdef COCOTB_SIM
`ifdef VCD
initial begin
 $dumpfile ("slave_dut.vcd");
 $dumpvars (0, slave);
 // Dump only first 16 vars of memories
 for (int i = 0; i < 16; i++) $dumpvars(0, DMA[i]);
 for (int i = 0; i < 16; i++) $dumpvars(0, SOCKET[i]);
end
`endif
`endif

endmodule: slave

