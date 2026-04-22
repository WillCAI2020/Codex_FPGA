`timescale 1ns/1ps

module tb_counter;
    reg clk;
    reg rst_n;
    wire [3:0] count;

    counter dut (
        .clk(clk),
        .rst_n(rst_n),
        .count(count)
    );

    initial begin
        clk = 1'b0;
        forever #5 clk = ~clk; // 10ns period
    end

    initial begin
        rst_n = 1'b0;
        #12;
        rst_n = 1'b1;
        // Extend simulation so rollover (15 -> 0) is observable.
        #240;
        $finish;
    end

    initial begin
        $dumpfile("counter.vcd");
        $dumpvars(0, tb_counter);
    end

    always @(posedge clk) begin
        $display("[%0t ns] rst_n=%0b count=%0d", $time, rst_n, count);
    end
endmodule
