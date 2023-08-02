from setuptools import setup
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='Luxbeam',
    version='v0.1.1',
    packages=['Luxbeam'],
    url='https://github.com/QITI/Luxbeam',
    license='',
    author='Chung-You Shih',
    author_email='c5shih@uwaterloo.ca',
    install_requires=[
        'numpy',
        'pillow',
    ],
    description='A python package that implements the protocol for programming Luxbeam '
                'DMD controller from VISITECH.',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
