from setuptools import setup

setup(
    name='Luxbeam',
    version='v0.1.0',
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
                'DMD controller from VISITECH.'
)
