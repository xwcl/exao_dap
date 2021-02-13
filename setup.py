from setuptools import setup
from os import path

HERE = path.abspath(path.dirname(__file__))
ORG = 'xwcl'
PROJECT = 'exao_dap'

with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

with open(path.join(HERE, PROJECT, 'VERSION'), encoding='utf-8') as f:
    VERSION = f.read().strip()

extras = {
    'dev': [
        'pytest',
        'werkzeug>=1.0.1,<2'
    ],
}
all_deps = set()
for _, deps in extras.items():
    for dep in deps:
        all_deps.add(dep)
extras['all'] = list(all_deps)

setup(
    name=PROJECT,
    version=VERSION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    packages=[PROJECT],
    python_requires='>=3.8, <4',
    install_requires=[
        'django>=3.1.5,<4',
        'social-auth-app-django>=4.0.0,<5',
        'django-extensions>=3.1.0,<4',
        'gunicorn>=20.0,<21',
        'fsspec>=0.8.5,<0.9',
        'irods-fsspec',
        'django-q>=1.3.4,<1.4'
    ],
    package_data={
        PROJECT: ['VERSION'],
    },
    extras_require=extras,
    project_urls={
        'Bug Reports': f'https://github.com/{ORG}/{PROJECT}/issues',
    },
)
