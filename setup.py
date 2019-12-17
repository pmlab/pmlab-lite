import setuptools, pathlib

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setuptools.setup(
	name='pmlab_lite',
    version='0.1.2',
    description='Process Mining scripting environment',
    long_description=README,
    long_description_content_type='text/markdown',
	classifiers=[
			'Development Status :: 2 - Pre-Alpha',
			'Programming Language :: Python :: 3'
		  ],
    url='https://github.com/pmlab/pmlab-lite',
    author=['Josep Carmona',
			'Matthias Weidlich',
			'Andrea Burattin',
			'jmunozgama',
			'Simon Remy'],
    author_email='',
    license='GPL-3.0',
    packages=setuptools.find_packages(),
    zip_safe=False
)
