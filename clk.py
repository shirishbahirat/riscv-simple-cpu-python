from myhdl import block, always_comb, concat, intbv, instances
from myhdl import instance, Signal, delay, modbv, always


@block
def clock_block(clock, period=20):

    lowTime = int(period / 2)
    highTime = period - lowTime

    @instance
    def clock_drive():
        while True:
            yield delay(lowTime)
            clock.next = 1
            yield delay(highTime)
            clock.next = 0

    return clock_drive


@block
def test_clock():

    clock = Signal(modbv(0)[1:])

    clk = clock_block(clock, period=20)
    clk.convert(hdl='Verilog')

    @instance
    def tester():
        yield delay(10)

    return instances()


test_inst = test_clock()
test_inst.config_sim(trace=True)
test_inst.run_sim(140)
