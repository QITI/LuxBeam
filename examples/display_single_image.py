import Luxbeam
from Luxbeam.sample import number_image

#  This is the equivalent example of displaying non-scrolling images in the LB 4600 user guide.

# Connect to the Luxbeam
luxbeam = Luxbeam.Luxbeam("192.168.0.10", timeout=1)  # modify the ip address if required.

# Prepare the image (display 123 on the DMD)
image = number_image(123, luxbeam.cols, luxbeam.rows)

# Set image type to 1 (binary). (One-time Operation)
luxbeam.set_image_type(1)

# Set inum size to 1080. (One-time Operation)
luxbeam.set_inum_size(luxbeam.rows)

# Disable the sequencer.
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.DISABLE)

# Set sequencer in reset-state
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.ENABLE)

# Load the image to inum = 0.
luxbeam.load_image(0, image)

# Compose the sequence file.
seq = Luxbeam.LuxbeamSequencer()
for _ in seq.jump_loop_iter():  # A while-true loop
    seq.load_global(0, 400)  # Load data from Inum (0) to DMD
    seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_INTERNAL, 0)  # Neg. edge internal trigger
    seq.reset_global(40)  # # Display contents on DMD

# View the generated sequence file
print(seq.dumps())

# Send sequence file.
luxbeam.load_sequence(seq.dumps())

# Take sequencer out of reset-state
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.DISABLE)

# Start the sequencer
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.ENABLE)
