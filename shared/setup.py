from setuptools import setup, find_packages

setup(
    name="my-shared-lib",          
    version="0.1.2",                
    packages=find_packages(),       
    install_requires=[              
        "sqlalchemy>=2.0",
        "aiosqlite",
    ],
)