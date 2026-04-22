`timescale 1ns / 1ps

module adc128s102_model (
    input  wire adc_cs_n,
    input  wire adc_sclk,
    input  wire adc_din,
    output wire adc_dout
);

reg [2:0] cmd_ch;
reg [2:0] pend_ch;
reg [4:0] pos_cnt;
reg [4:0] neg_cnt;
integer frame_idx;
reg frame_active;

function [11:0] sample_fn;
    input [2:0] ch;
    input integer idx;
    begin
        sample_fn = (({9'd0, ch} * 12'h111) + (idx * 12'h013)) & 12'hFFF;
    end
endfunction

wire [11:0] cur_data;
assign cur_data = sample_fn(pend_ch, frame_idx);

assign adc_dout = (!adc_cs_n && (pos_cnt >= 5'd4) && (pos_cnt <= 5'd15))
                ? cur_data[15 - pos_cnt]
                : 1'b0;

always @(negedge adc_cs_n) begin
    pos_cnt <= 5'd0;
    neg_cnt <= 5'd0;
    cmd_ch <= 3'd0;
    frame_active <= 1'b1;
end

always @(posedge adc_sclk) begin
    if(!adc_cs_n)
        pos_cnt <= pos_cnt + 1'b1;
end

// ADC128S102 latches channel control bits on falling SCLK edges.
always @(negedge adc_sclk) begin
    if(!adc_cs_n) begin
        if(neg_cnt == 5'd2) cmd_ch[2] <= adc_din; // falling #3
        if(neg_cnt == 5'd3) cmd_ch[1] <= adc_din; // falling #4
        if(neg_cnt == 5'd4) cmd_ch[0] <= adc_din; // falling #5
        neg_cnt <= neg_cnt + 1'b1;
    end
end

always @(posedge adc_cs_n) begin
    if(frame_active) begin
        pend_ch <= cmd_ch;
        frame_idx <= frame_idx + 1;
        frame_active <= 1'b0;
    end
end

initial begin
    cmd_ch = 3'd0;
    pend_ch = 3'd0;
    pos_cnt = 5'd0;
    neg_cnt = 5'd0;
    frame_idx = 0;
    frame_active = 1'b0;
end

endmodule
