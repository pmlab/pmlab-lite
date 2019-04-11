import setuptools

setuptools.setup(
	name='pmlab_lite',
    version='0.1.1',
    description='Process Mining scripting environment',
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
