import Luxbeam

# This example shows how one can use LuxbeamSequencer to program the LuxBeam sequencer code with python.

seq = Luxbeam.LuxbeamSequencer()

reg0 = seq.assign_var_reg(regno=0)  # Assign register 0
for _ in seq.jump_loop_iter():  # While-True loop
    seq.load_global(0, 400)  # Load the image 0
    for _, inum in seq.range_loop_iter(0, reg0):  # inum changes from 0 to register_0
        seq.reset_global(40)  # Display the image
        seq.load_global(inum + 1, 400)  # Load the image inum+1
        seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_SOFTWARE + Luxbeam.TRIG_SOURCE_ELECTRICAL,
                 0)  # Waiting for negative software or electrical trigger

print(seq.dumps())
"""
Generated sequencer code: 

AssignVar ConstVar0 0 1
AssignVarReg Var0 0 1
Label Loop0 1
LoadGlobal ConstVar0 400
AssignVar Var1 0 1
Label Loop_1 1
ResetGlobal 40
AssignVar Var2 1 1
Add Var2 Var1 1
LoadGlobal Var2 400
Trig 1 9 0
Add Var1 1 1
JumpIf Var1 < Var0 Loop_1 1
Jump Loop0 1
"""