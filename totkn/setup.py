from setuptools import setup, find_packages

setup(
    name="totkn",
    version="0.1.0",
    license="proprietary",
    description="to tekton files",
    author="Powell Quiring",
    author_email="powellquiring@gmail.com",
    url="https://powellquiring.com",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=["click"],
    entry_points={"console_scripts": ["totkn = totkn:cli",]},
)
