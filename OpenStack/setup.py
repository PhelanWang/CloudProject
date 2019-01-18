# coding: utf-8

from setuptools import setup, find_packages

setup(
    name="OpenStackTest",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        "console_scripts": [
            "openstack_start = OpenStackTest.command.execute:start_openstack_test",
            "openstack_test_init = OpenStackTest.command.execute:init"
        ]
    }
)