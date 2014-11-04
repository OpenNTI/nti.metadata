import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
    'console_scripts': [
        "nti_metadata_processor = nti.metadata.utils.processor:main",
    ],
    "z3c.autoinclude.plugin": [
		'target = nti.dataserver'
	],
}

setup(
    name='nti.metadata',
    version=VERSION,
    author='Josh Zuech',
    author_email='josh.zuech@nextthought.com',
    description="NTI processor that updates metadata indexes.",
    long_description=codecs.open('README.rst', encoding='utf-8').read(),
    license='Proprietary',
    keywords='pyramid preference',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
		'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        ],
	packages=find_packages('src'),
	package_dir={'': 'src'},
	namespace_packages=['nti'],
	install_requires=[
		'setuptools',
        'zc.catalogqueue'
	],
	entry_points=entry_points
)
