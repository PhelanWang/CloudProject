# coding: utf-8

from setuptools import setup, find_packages

setup(
    name="CloudTest",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "node_start = CloudTest.command.execute:start_node",
            "engine_start = CloudTest.command.execute:start_engine",
            "cloud_node_init = CloudTest.command.execute:node_init",
            "cloud_engine_init = CloudTest.command.execute:engine_init"
        ]
    }
)