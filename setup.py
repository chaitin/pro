import os
from setuptools import setup

# quick and dirty build for antlr
os.system('which antlr4 && cd pro/parse && antlr4 -no-listener -visitor -Dlanguage=Python2 pro.g4')

setup(
    name='pro',
    version='1.0',
    description='PROgramming ROP like a PRO',
    packages=['pro', 'pro.parse'],
    install_requires=[
        'jinja2',
        'antlr4-python2-runtime',
    ],
)
