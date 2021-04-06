import Luxbeam
from Luxbeam.sample import number_image
import numpy as np
#  This is the equivalent example of displaying non-scrolling images in LB 4600 in the user guide.

# Connect to the Luxbeam
luxbeam = Luxbeam.Luxbeam("dmd.qiti", timeout=1) # modify the ip address if required.

# Prepare the image (display 123 on the DMD)
image = np.zeros(shape=(luxbeam.rows, luxbeam.cols), dtype=np.bool)


# Disable the sequencer.
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.DISABLE)

# Set sequencer in reset-state
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.ENABLE)
