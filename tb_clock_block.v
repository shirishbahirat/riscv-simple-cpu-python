module tb_clock_block;

wire [0:0] clock;

initial begin
    $to_myhdl(
        clock
    );
end

clock_block dut(
    clock
);

endmodule
