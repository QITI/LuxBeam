import Luxbeam


def test_connection(luxbeam_ip):
    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)

def test_load_sequence(luxbeam_ip):
    seq = """#-------------------------------------------------------------------------------------
#Command Parameters Waitfor Comment
#-------------------------------------------------------------------------------------
AssignVar Inum 0 1 # Inum = 0
Label StartHere 1 # Start of loop
LoadGlobal Inum 400 # Load data from Inum (0) to DMD
Trig 1 4 0 # Neg. edge internal trigger
ResetGlobal 40 # Display contents on DMD
Jump StartHere 1 # Jump to start of loop"""

    print(seq)
    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)
    try:
        luxbeam.load_sequence(seq)
    except Exception as err:
        print(luxbeam.get_sequencer_file_error_log())
        raise err


def test_sequencer(luxbeam_ip):
    seq = Luxbeam.LuxbeamSequencer()

    inum = seq.assign_var(0)
    for _ in seq.jump_loop_iter():
        seq.load_global(inum, 400)
        seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_INTERNAL, 0)
        seq.reset_global(40)
    #seq.reset_global(40)
    print(seq.dumps())

    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)
    try:
        luxbeam.load_sequence(seq.dumps())
    except Exception as err:
        print(luxbeam.get_sequencer_file_error_log())
        raise err