from setuptools import setup, find_packages

setup(
    name='microserver',
    version='0.1.0',
    packages=find_packages(exclude=('tests',)),
    install_requires=['flask==2.0.3', 'Werkzeug==2.2.2'],
    python_requires='>=3.7',
    entry_points=dict(
        console_scripts=['microserver=microserver.__main__:main']
    )
)
