from setuptools import setup, find_packages

setup(
    name='ibmcli',
    version='0.1.0',
    license='proprietary',
    description='more complicated stuff then ibmcloud cli',

    author='Powell Quiring',
    author_email='powellquiring@gmail.com',
    url='https://powellquiring.com',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=['click'],

    entry_points={
        'console_scripts': [
            'ibmcli = ibmcli.cli:cli',
        ]
    },
)

