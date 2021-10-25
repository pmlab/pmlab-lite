import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pmlab_lite',
    version='0.4.9.1',
    author=['Josep Carmona',
            'Matthias Weidlich',
            'Andrea Burattin',
            'jmunozgama',
            'Simon Remy',
            'Glenn Dittmann'],
    author_email='',
    description='Process Mining scripting environment',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/pmlab/pmlab-lite',
    packages=setuptools.find_packages(),
    license='GPL-3.0',
    python_requires=">=3.7",
    install_requires=[
            'numpy',
            'graphviz',
            'tqdm',
            'lxml',
            'ortools',
        ],
    classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Programming Language :: Python :: 3',
          ],
)
