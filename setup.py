from setuptools import setup

try:
    from sphinx.setup_command import BuildDoc
    sphinx_imported = True
except BaseException:
    sphinx_imported = False

name = 'dynrat'
version = '0.0'
release = '0.0.1'
dev_status = 'Development Status :: 1 - Planning'

install_requires = ['numpy==1.18.1',
                    'pandas==1.0.1', 'scipy==1.4.1', 'tables==3.6.1']

setup_kwargs = {
    'name': name,
    'version': release,
    'packages': ['dynrat'],
    'url': 'https://code.usgs.gov/dynamic-rating/dynrat',
    'license': 'License :: Public Domain',
    'author': 'Marian Domanski',
    'author_email': 'mdomanski@usgs.gov',
    'description': 'Dynamic rating',
    'classifiers': [
        dev_status,
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Hydrology'
    ],
    'python_requires': '~=3.7',
    'install_requires': install_requires
}

if sphinx_imported:
    cmdclass = {'build_sphinx': BuildDoc}
    docs_source = 'docs/'
    docs_build_dir = 'docs/_build'
    docs_builder = 'html'
    setup_kwargs['command_options'] = {'build_sphinx': {
        'project': ('setup.py', name),
        'version': ('setup.py', version),
        'release': ('setup.py', release),
        'source_dir': ('setup.py', docs_source),
        'build_dir': ('setup.py', docs_build_dir),
        'builder': ('setup.py', docs_builder)}}

setup(**setup_kwargs)
