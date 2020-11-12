from setuptools import setup

setup(
    name='hey',
    version='0.1',
    install_requires=[
        'requests',
        'tabulate'
    ],
    entry_points='''
        [console_scripts]
        hey=hey:cli
    ''',
)
