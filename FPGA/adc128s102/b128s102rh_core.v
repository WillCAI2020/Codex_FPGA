`timescale 1ns / 1ps
// -----------------------------------------------------------------------------
// B128S102RH / ADC128S102 single-conversion SPI core
// -----------------------------------------------------------------------------
module b128s102rh_core
#(
    parameter integer CLK_FREQ_HZ = 50_000_000,
    parameter integer SCLK_HZ     = 5_000_000
)(
    input  wire        clk,
    input  wire        rst_n,

    input  wire        req,
    input  wire [2:0]  req_ch,

    input  wire        adc_dout,
    output reg         adc_cs_n,
    output reg         adc_sclk,
    output reg         adc_din,

    output wire        busy,
    output reg         done,
    output reg [11:0]  data,
    output reg [2:0]   ret_ch
);

localparam integer SCLK_DIV = CLK_FREQ_HZ / SCLK_HZ;
localparam integer HALF_DIV = SCLK_DIV / 2;

localparam [3:0] st_idle  = 4'b0001;
localparam [3:0] st_start = 4'b0010;
localparam [3:0] st_shift = 4'b0100;
localparam [3:0] st_stop  = 4'b1000;

reg [3:0] cur_state;
reg [3:0] next_state;

assign busy = (cur_state != st_idle);

reg [15:0] div_cnt;
reg [5:0]  edge_cnt;
reg [11:0] shreg;
reg [2:0]  latched_req_ch;
reg [2:0]  pend_ch;

wire st_shift_last_edge;
assign st_shift_last_edge = (cur_state == st_shift) && (div_cnt == HALF_DIV - 1) && (edge_cnt == 6'd31);

always @(posedge clk or negedge rst_n) begin
    if(!rst_n)
        cur_state <= st_idle;
    else
        cur_state <= next_state;
end

always @(*) begin
    case(cur_state)
        st_idle:  next_state = req ? st_start : st_idle;
        st_start: next_state = st_shift;
        st_shift: next_state = st_shift_last_edge ? st_stop : st_shift;
        st_stop:  next_state = st_idle;
        default:  next_state = st_idle;
    endcase
end

always @(posedge clk or negedge rst_n) begin
    if(!rst_n) begin
        adc_cs_n       <= 1'b1;
        adc_sclk       <= 1'b1;
        adc_din        <= 1'b0;
        done           <= 1'b0;
        data           <= 12'd0;
        ret_ch         <= 3'd0;
        latched_req_ch <= 3'd0;
        pend_ch        <= 3'd0;
        shreg          <= 12'd0;
        div_cnt        <= 16'd0;
        edge_cnt       <= 6'd0;
    end else begin
        done <= 1'b0;

        case(cur_state)
            st_idle: begin
                adc_cs_n <= 1'b1;
                adc_sclk <= 1'b1;
                adc_din  <= 1'b0;
                div_cnt  <= 16'd0;
                edge_cnt <= 6'd0;
                shreg    <= 12'd0;
                if(req)
                    latched_req_ch <= req_ch;
            end

            st_start: begin
                adc_cs_n <= 1'b0;
                adc_sclk <= 1'b1;
                adc_din  <= 1'b0;
                div_cnt  <= 16'd0;
                edge_cnt <= 6'd0;
            end

            st_shift: begin
                if(div_cnt == HALF_DIV - 1) begin
                    div_cnt <= 16'd0;
                    case(edge_cnt)
                        6'd0: adc_sclk <= 1'b0;
                        6'd1: adc_sclk <= 1'b1;
                        6'd2: adc_sclk <= 1'b0;
                        6'd3: begin adc_sclk <= 1'b1; adc_din <= latched_req_ch[2]; end
                        6'd4: adc_sclk <= 1'b0;
                        6'd5: begin adc_sclk <= 1'b1; adc_din <= latched_req_ch[1]; end
                        6'd6: adc_sclk <= 1'b0;
                        6'd7: begin adc_sclk <= 1'b1; adc_din <= latched_req_ch[0]; end
                        6'd8: adc_sclk <= 1'b0;
                        6'd9:  begin adc_sclk <= 1'b1; shreg[11] <= adc_dout; end
                        6'd10: adc_sclk <= 1'b0;
                        6'd11: begin adc_sclk <= 1'b1; shreg[10] <= adc_dout; end
                        6'd12: adc_sclk <= 1'b0;
                        6'd13: begin adc_sclk <= 1'b1; shreg[9]  <= adc_dout; end
                        6'd14: adc_sclk <= 1'b0;
                        6'd15: begin adc_sclk <= 1'b1; shreg[8]  <= adc_dout; end
                        6'd16: adc_sclk <= 1'b0;
                        6'd17: begin adc_sclk <= 1'b1; shreg[7]  <= adc_dout; end
                        6'd18: adc_sclk <= 1'b0;
                        6'd19: begin adc_sclk <= 1'b1; shreg[6]  <= adc_dout; end
                        6'd20: adc_sclk <= 1'b0;
                        6'd21: begin adc_sclk <= 1'b1; shreg[5]  <= adc_dout; end
                        6'd22: adc_sclk <= 1'b0;
                        6'd23: begin adc_sclk <= 1'b1; shreg[4]  <= adc_dout; end
                        6'd24: adc_sclk <= 1'b0;
                        6'd25: begin adc_sclk <= 1'b1; shreg[3]  <= adc_dout; end
                        6'd26: adc_sclk <= 1'b0;
                        6'd27: begin adc_sclk <= 1'b1; shreg[2]  <= adc_dout; end
                        6'd28: adc_sclk <= 1'b0;
                        6'd29: begin adc_sclk <= 1'b1; shreg[1]  <= adc_dout; end
                        6'd30: adc_sclk <= 1'b0;
                        6'd31: begin adc_sclk <= 1'b1; shreg[0]  <= adc_dout; end
                        default: adc_sclk <= 1'b1;
                    endcase

                    if(edge_cnt != 6'd31)
                        edge_cnt <= edge_cnt + 1'b1;
                end else begin
                    div_cnt <= div_cnt + 1'b1;
                end
            end

            st_stop: begin
                adc_cs_n <= 1'b1;
                adc_sclk <= 1'b1;
                adc_din  <= 1'b0;
                div_cnt  <= 16'd0;
                edge_cnt <= 6'd0;

                data   <= shreg;
                ret_ch <= pend_ch;
                done   <= 1'b1;
                pend_ch <= latched_req_ch;
            end

            default: begin
                adc_cs_n <= 1'b1;
                adc_sclk <= 1'b1;
                adc_din  <= 1'b0;
                div_cnt  <= 16'd0;
                edge_cnt <= 6'd0;
                shreg    <= 12'd0;
            end
        endcase
    end
end

endmodule
