import codecs
from setuptools import setup, find_packages

VERSION = '0.0.0'

entry_points = {
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
        'Programming Language :: Python :: 2.7'
        'Programming Language :: Python :: Implementation :: CPython'
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['nti'],
    install_requires=[
        'setuptools',
        'nti.async',
        'nti.coremetadata',
        'nti.site',
        'nti.zodb',
        'nti.zope_catalog',
        'zc.catalogqueue',
        'zope.catalog',
        'zope.component',
        'zope.deprecation',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.security',
    ],
    entry_points=entry_points
)
