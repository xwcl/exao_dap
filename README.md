# The ExAO Data Analysis Platform: service component

The web services here provide access to a registry of datasets and a grid execution platform deployed at https://dap.xwcl.science.

## Secrets

Production secrets are stored in a KeePass archive in the team Box folder.

### Generating secrets

  * See `cyverse.py` docstring for creating CyVerse OAuth2 secrets
  * Regenerate deploy key with `ssh-keygen -t ed25519 -N "" -f secrets/id_ed25519_deploy` and update `users.extraUsers.exao_dap.openssh.authorizedKeys` in `dap_infrastructure/configuration.nix`

## URLs

Browser:

GET ingest/
GET ingest/?path=foo
POST ingest/
GET <pk>/
POST <pk>/finalize/

end user API:

POST ingest/  with optional webhook
GET <pk>
POST <pk>/finalize/  (commit or discard; cancel workers if needed)

internal API:

(stage in data)
POST /datasets/
(begin syncing datums)

Trigger summary job on completion? have sync tasks query for bigjobs that have this dataset identifier as input and trigger if prereqs are all met

```
/registrar/datasets/ingest/  (browser, end-user api client)
GET -> path validate -> full form
-> POST -> convert to serializer, save

/registrar/datasets/<pk>/ (view, create with internal api client from jobs)
GET -> template
POST -> validate service account in DRF -> create dataset and datums -> launch ingest tasks for every datum

states for a dataset:

user-submitted (syncing) -> user-confirmed
platform-submitted -> platform-complete

/registrar/datasets/<pk>/commit/
/registrar/data/
/undertaker/grid/
/undertaker/bigjob/
```

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

## Spec


## Job

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



./klipReduce --minDPx 3 --iwapx 10 --owapx 30 -D ./inputs/
-> produce outfile.fits

[
    '--minDPx',
    {'kind': 'set', 'values': [3, 4, 5]},
    '--iwapx',
    {'kind': 'set', 'values': [10, 12, 14]},
    '--owapx',
    '30',
    '-D',
    {'kind': 'datum', 'path': '/full/irods/path/file.fits'} # stage one file in
    {'kind': 'folder_from_filter', 'value': '?foo=bar'}, # stage all matching files into a new folder
    {'kind': 'set_from_filter', 'value': '?foo=bar'},   # make a job for each entry in the filter output
    {'kind': 'folder_from_dataset', 'path': '/full/irods/path/collection'},  # stage this irods path into a folder
]
[
    '--minDPx',
    '3',
    '--iwapx',
    '10'
    '--owapx',
    '30',
    '-D',
    {'kind': 'folder', ['id1', 'id2', 'id3']},
]
