from setuptools import setup

setup(
    name='TCP',
    version='1.0',
    packages=['generator'],  # same as name
    install_requires=[
        'magenta',
        'tensorflow',
        'note_seq',
        'music21',
        'autopep8',
        'beautifulsoup4',
        'lxml'
    ],  # external packages as dependencies
)
