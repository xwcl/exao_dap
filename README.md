# The ExAO Data Analysis Platform web application

## Setup for local development

### macOS with Homebrew

* `brew install postgres`
* `brew services start postgresql`
```
$ psql postgres
psql (13.1)
Type "help" for help.

postgres=# create database exao_dap;
CREATE DATABASE
```

### dependencies

* psycopg2
* django

### Job Grid and Args Spec

grid

```
[
    '--foo',
    {'kind': 'data_from_filter', 'value': '?foo=bar'},
    {'kind': 'data', 'value': {'irods:///foo/bar': 'bar', 'irods:///foo/baz': 'baz'},
    {'kind': 'data_from_filter', 'value_set': ['?foo=bar', '?foo=baz']},
    {'kind': 'data', 'value_set': [
        {'irods:///foo/bar': 'bar', 'irods:///foo/baz': 'baz'},
        {'irods:///foo/quux': 'quux', 'irods:///foo/heck': 'heck'},
    ]}
    '--minDPx',
    {'kind': 'literal', 'value_set': [1, 2, 3]},
]
```

conversion from grid spec to job spec involves flattening 'value_set's into values and 'data_from_filter' into 'data'

```
[
    '--foo',
    {'kind': 'data', 'value': {'irods:///foo/bar': 'bar', 'irods:///foo/baz': 'baz'},
    {'kind': 'data', 'value': {'irods:///foo/quux': 'quux', 'irods:///foo/heck': 'heck'}},
    '--minDPx',
    {'kind': 'literal', 'value': 1},
]
```

grid spec -> single job spec with filters -> job spec with data path mappings -> args spec with literal strings
