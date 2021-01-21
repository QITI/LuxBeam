# LuxBeam
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
Run the test in the test folder:
```
pytest test --ip="<IP address>"
```
Run the test with interactive tests:
```
pytest test --ip="<IP address>" --interactive -s
```