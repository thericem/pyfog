# coding: utf-8
'''
@author: jamwheeler
'''

from setuptools import setup, find_packages

setup(
    name='pyfog',
    version="0.0.1",
    author='Jonathan Wheeler',
    author_email='jamwheeler@stanford.edu',
    url='http://github.com/wheelerj/pyfog',
    packages=find_packages(),
    description='Python Fiber Optic Gyro Toolkit',
    long_description='Tools for handling instrumentation, data acquisition, and analysis of fiber optic gyros',
    install_requires=['pyvisa',
                      'numpy',
                      'PyDAQmx',
                      'pyserial',
                      'matplotlib'],

)
