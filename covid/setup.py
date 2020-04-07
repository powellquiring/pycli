from setuptools import setup, find_packages

setup(
    name="covid",
    version="0.1.0",
    license="proprietary",
    description="ibmcloud login",
    author="Powell Quiring",
    author_email="powellquiring@gmail.com",
    url="https://powellquiring.com",
    packages=find_packages(where="."),
    package_dir={"": "."},
    install_requires=["click"],
    entry_points={"console_scripts": ["covid = covid:cli",]},
)
