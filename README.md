# Luxbeam Introduction
[![Build Documentation HTML](https://github.com/QITI/Luxbeam/actions/workflows/python-package.yml/badge.svg)](https://github.com/QITI/Luxbeam/actions/workflows/python-package.yml)

`Luxbeam` is a python package that implements the protocol for programming [Luxbeam DMD controller](https://www.keynotephotonics.com/dlp-chipsets/#CHIPSET-DLP9500) from [VISITECH](https://visitech.no/).
The `Luxbeam` class implements the control protocol of Luxbeam digital micro-mirror device (DMD) controller. 
This is tested with Luxbeam 4600 controller and DLP9500UV DMD.
In addition to equipment control from the `Luxbeam` class, the `LuxbeamSeqeuncer` class implements the support for composing sequencer code used in Luxbeam controller.
This allows the user to compose the sequencer code using native python arithmetic operations and some of the flow controls. 

## Installation
One can install the package via setuptools:
```
python setup.py install
```
To install the package in [develop mode](https://stackoverflow.com/questions/19048732/python-setup-py-develop-vs-install) instead, use:
```
python setup.py develop
```

## Test
It is recommended to run the test cases to ensure `LuxBeam` is compatiable with your setup.

Run the tests in the test folder:
```
pytest test --ip="<IP address>"
```
Run the interactive tests:
```
pytest test --ip="<IP address>" --interactive -s
```

## Example
```python
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

# Compose the sequencer file.
seq = Luxbeam.LuxbeamSequencer()
for _ in seq.jump_loop_iter():  # A while-true loop
    seq.load_global(0, 400)  # Load data from Inum (0) to DMD
    seq.trig(Luxbeam.TRIG_MODE_NEGATIVE_EDGE, Luxbeam.TRIG_SOURCE_INTERNAL, 0)  # Neg. edge internal trigger
    seq.reset_global(40)  # Display contents on DMD

# View the generated sequence file
print(seq.dumps())

# Send sequence file.
luxbeam.load_sequence(seq.dumps())

# Take sequencer out of reset-state
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RESET, Luxbeam.DISABLE)

# Start the sequencer
luxbeam.set_sequencer_state(Luxbeam.SEQ_CMD_RUN, Luxbeam.ENABLE)
```

