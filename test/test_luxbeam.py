import Luxbeam
from Luxbeam.sample import number_image
import pytest
import time
import random


def yesno(question):
    """Simple Yes/No Function."""
    prompt = f'{question} ? (y/n): '
    ans = input(prompt).strip().lower()
    if ans not in ['y', 'n']:
        print(f'{ans} is invalid, please try again...')
        return yesno(question)
    if ans == 'y':
        return True
    return False


def test_connection(luxbeam_ip):
    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)


def test_sequencer_reg(luxbeam_ip):
    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)
    reg_no = random.randint(0, 11)
    reg_val_send = random.randint(0, 65535)
    luxbeam.set_sequencer_reg(reg_no, reg_val_send)
    reg_val_recv = luxbeam.get_sequencer_reg(reg_no)
    assert reg_val_recv == reg_val_send


def test_software_sync(luxbeam_ip):
    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)
    level = luxbeam.get_software_sync()
    level_new_send = 1 if level == 0 else 0
    luxbeam.set_software_sync(level_new_send)
    level_new_recv = luxbeam.get_software_sync()
    assert level_new_send == level_new_recv
    assert level != level_new_recv
    luxbeam.set_software_sync(level)


@pytest.mark.skip
def test_sequencer(luxbeam_ip):
    seq = Luxbeam.LuxbeamSequencer()

    # TODO implement load default sequencer

    inum = seq.assign_var(0)
    for _ in seq.jump_loop_iter():
        seq.load_global(inum, 400)
        seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_INTERNAL, 0)
        seq.reset_global(40)
    # seq.reset_global(40)
    print(seq.dumps())

    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)

    try:
        luxbeam.load_sequence(seq.dumps())
    except Exception as err:
        print(luxbeam.get_sequencer_file_error_log())
        raise err


@pytest.mark.interactive
def test_load_single(luxbeam_ip):
    seq = Luxbeam.LuxbeamSequencer()

    # ======= Sequencer ============
    inum = seq.assign_var(0)
    for _ in seq.jump_loop_iter():
        seq.load_global(inum, 400)
        seq.reset_global(40)
        seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_NONE, 0)
    # ======= Sequencer ============

    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)

    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.DISABLE)

    number_to_display = random.randint(100, 999)

    img0 = number_image(number_to_display, luxbeam.cols, luxbeam.rows)

    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.ENABLE)
    try:
        luxbeam.load_sequence(seq.dumps())
    except Exception as err:
        print(seq.dumps())
        print(luxbeam.get_sequencer_file_error_log())
        raise err
    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.DISABLE)

    luxbeam.load_image(0, img0)
    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.ENABLE)

    assert yesno("Is number {0} displayed on the DMD".format(number_to_display))


@pytest.mark.interactive
def test_load_multiple(luxbeam_ip):
    NUM_IMAGE = 3
    seq = Luxbeam.LuxbeamSequencer()

    # ======= Sequencer ============
    reg0 = seq.assign_var_reg(regno=0)
    for _ in seq.jump_loop_iter():
        seq.load_global(0, 400)
        for _, inum in seq.range_loop_iter(0, reg0):
            seq.reset_global(40)
            seq.load_global(inum + 1, 400)
            seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_SOFTWARE, 0)
    # ======= Sequencer ============
    """
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
    Trig 1 8 0
    Add Var1 1 1
    JumpIf Var1 < Var0 Loop_1 1
    Jump Loop0 1
    """

    luxbeam = Luxbeam.Luxbeam(luxbeam_ip, timeout=1)

    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.DISABLE)
    luxbeam.set_software_sync(0)

    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.ENABLE)
    try:
        luxbeam.load_sequence(seq.dumps())
    except Exception as err:
        print(seq.dumps())
        print(luxbeam.get_sequencer_file_error_log())
        raise err

    luxbeam.set_sequencer_reg(0, NUM_IMAGE)

    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.DISABLE)

    def test_num_image(num_image):
        numbers = [random.randint(100, 999) for _ in range(num_image)]
        images = [number_image(n, luxbeam.cols, luxbeam.rows) for n in numbers]

        for i, img in enumerate(images):
            luxbeam.load_image(i, img)

        luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.ENABLE)

        for i in range(NUM_IMAGE):
            assert yesno("Is number {0} displayed on the DMD".format(numbers[i]))
            luxbeam.set_software_sync(1)
            time.sleep(0.01)
            luxbeam.set_software_sync(0)

        assert yesno("Is number {0} displayed on the DMD".format(numbers[0]))

    test_num_image(NUM_IMAGE)

    NUM_IMAGE = 2
    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.DISABLE)
    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.ENABLE)
    luxbeam.set_sequencer_reg(0, NUM_IMAGE)
    luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.DISABLE)
    test_num_image(NUM_IMAGE)
