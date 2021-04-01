import Luxbeam

# This example shows how one can use LuxbeamSequencer to program the LuxBeam sequencer code with python.

seq = Luxbeam.LuxbeamSequencer()
for l, inum in seq.range_loop_iter(5):
    seq.load_global(inum, 400)
    seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_SOFTWARE, 0)
    seq.reset_global(40)
print(seq.dumps())
