from setuptools import find_packages, setup

print(find_packages())

setup(
    name='quantylab-systrader',
    version='1.0',
    description='System trading for Quantylab',
    author='Quantylab',
    author_email='quantylab@gmail.com',
    url='https://github.com/quantylab/quantylab-systrader',
    packages=find_packages(),
    install_requires=[
        'django', 'pywinauto'
    ]
)