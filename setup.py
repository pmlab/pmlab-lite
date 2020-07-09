from distutils.core import setup

setup(
	name='pmlab_lite',
    version='0.3.9.8',
    license='GPL-3.0',
    description='Process Mining scripting environment',
    author=['Josep Carmona',
			'Matthias Weidlich',
			'Andrea Burattin',
			'jmunozgama',
			'Simon Remy',
			'Glenn Dittmann'],
    author_email='',
    url='https://github.com/pmlab/pmlab-lite',
	install_requires=[
    		'numpy',
    		'graphviz',
    		'tqdm',
    	], #maybe pythone-dateutil
	classifiers=[
			'Development Status :: 2 - Pre-Alpha',
			'Programming Language :: Python :: 3',
		  ],
)
