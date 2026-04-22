`timescale 1ns / 1ps

module tb_b128s102rh_core;
    reg clk;
    reg rst_n;
    reg req;
    reg [2:0] req_ch;

    wire adc_cs_n;
    wire adc_sclk;
    wire adc_din;
    wire adc_dout;

    wire busy;
    wire done;
    wire [11:0] data;
    wire [2:0] ret_ch;

    integer done_count;
    integer err_count;
    integer i;
    reg [2:0] req_hist [0:63];

    b128s102rh_core #(
        .CLK_FREQ_HZ(50_000_000),
        .SCLK_HZ(5_000_000)
    ) dut (
        .clk(clk),
        .rst_n(rst_n),
        .req(req),
        .req_ch(req_ch),
        .adc_dout(adc_dout),
        .adc_cs_n(adc_cs_n),
        .adc_sclk(adc_sclk),
        .adc_din(adc_din),
        .busy(busy),
        .done(done),
        .data(data),
        .ret_ch(ret_ch)
    );

    adc128s102_model adc_model (
        .adc_cs_n(adc_cs_n),
        .adc_sclk(adc_sclk),
        .adc_din(adc_din),
        .adc_dout(adc_dout)
    );

    function [11:0] sample_fn;
        input [2:0] ch;
        input integer idx;
        begin
            sample_fn = (({9'd0, ch} * 12'h111) + (idx * 12'h013)) & 12'hFFF;
        end
    endfunction

    function [2:0] pattern_ch;
        input integer idx;
        begin
            pattern_ch = (idx * 3 + 1) % 8;
        end
    endfunction

    function [2:0] expected_ch;
        input integer idx;
        begin
            if(idx == 0)
                expected_ch = 3'd0;
            else
                expected_ch = req_hist[idx-1];
        end
    endfunction

    initial begin
        clk = 1'b0;
        forever #10 clk = ~clk; // 50MHz
    end

    initial begin
        rst_n = 1'b0;
        req = 1'b0;
        req_ch = 3'd0;
        done_count = 0;
        err_count = 0;

        #200;
        rst_n = 1'b1;

        // Issue 24 single-cycle requests, only when core is idle.
        for(i = 0; i < 24; i = i + 1) begin
            while(busy) @(posedge clk);
            req_ch = pattern_ch(i);
            req_hist[i] = req_ch;
            req = 1'b1;
            while(!busy) @(posedge clk);
            req = 1'b0;
        end
    end

    always @(posedge clk) begin
        if(rst_n && done) begin
            $display("[DONE %0d] ret_ch=%0d data=0x%03h expected_ch=%0d expected_data=0x%03h",
                     done_count, ret_ch, data, expected_ch(done_count), sample_fn(expected_ch(done_count), done_count));

            if(ret_ch !== expected_ch(done_count)) begin
                $display("ERROR: ret_ch mismatch at frame %0d", done_count);
                err_count <= err_count + 1;
            end
            if(data !== sample_fn(expected_ch(done_count), done_count)) begin
                $display("ERROR: data mismatch at frame %0d", done_count);
                err_count <= err_count + 1;
            end

            done_count <= done_count + 1;

            if(done_count == 23) begin
                #200;
                if(err_count == 0)
                    $display("TB PASS: %0d frames verified", done_count + 1);
                else
                    $display("TB FAIL: err_count=%0d", err_count);
                $finish;
            end
        end
    end

    initial begin
        $dumpfile("adc128s102.vcd");
        $dumpvars(0, tb_b128s102rh_core);
    end

    initial begin
        #3000000;
        $display("TB TIMEOUT");
        $finish;
    end

endmodule
