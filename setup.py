import codecs
from setuptools import setup
from setuptools import find_packages

entry_points = {
    "z3c.autoinclude.plugin": [
        'target = nti.dataserver'
    ],
}

TESTS_REQUIRE = [
    'fakeredis',
    'fudge',
    'nti.testing',
    'zope.testrunner',
    'zope.dottedname',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.metadata',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI processor that updates metadata indexes",
    long_description=(_read('README.rst') + '\n\n' + _read('CHANGES.rst')),
    license='Apache',
    keywords='metadata',
    classifiers=[
        'Framework :: Zope',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/NextThought/nti.metadata",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'nti.asynchronous',
        'nti.async',
        'nti.coremetadata',
        'nti.site',
        'nti.zodb',
        'nti.zope_catalog',
        'persistent',
        'six',
        'zope.catalog',
        'zope.component',
        'zope.deprecation',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.security',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
        'docs': [
            'Sphinx',
            'repoze.sphinx.autointerface',
            'sphinx_rtd_theme',
        ],
    },
    entry_points=entry_points,
)
