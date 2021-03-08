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
(begin syncing data)

Trigger summary job on completion? have sync tasks query for bigjobs that have this dataset identifier as input and trigger if prereqs are all met

```
/registrar/datasets/ingest/  (browser, end-user api client)
GET -> path validate -> full form
-> POST -> convert to serializer, save

/registrar/datasets/<pk>/ (view, create with internal api client from jobs)
GET -> template
POST -> validate service account in DRF -> create dataset and data -> launch ingest tasks for every datum

states for a dataset:

user-submitted (syncing) -> user-confirmed
platform-submitted -> platform-complete

/registrar/datasets/
/registrar/datasets/ingest/
/registrar/datasets/
/registrar/datasets/<identifier>/data/<filename>/

/registrar/query/

/registrar/data/<pk>/
/registrar/data/<pk>/view/
/registrar/data/<pk>/download/
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
    {'kind': 'file', 'path': '/path/to...'},   # evaluate ACLs when generating, then the path can be just the path
    {'kind': 'folder', ['/path/1', '/path/b/2', '/path/c/1']},

]


## Template

  * name
  * template
  * state [draft, finalized]

## Job

  * id
  * template nullable
  * spec
  * state [draft, submitted, executing, failed, complete]

## Stage in and stage out

batch script looks like:

DAP_TOKEN=token
dap_execute https://dap.xwcl.science/jobs/id/

### Stage in

1. Invoke CLI client with token and job ID
2. Retrieve job payload
3. POST place job in 'executing'
3. Construct command line:
    * literal: push on to args list
    * 'datum'
        1. retrieve one file and store at unique path (checksum + extension), push path onto args list
    * 'folder'
        1. make unique folder name somehow
        2. retrieve each file into that folder
        3. push folder path onto args list
4. Invoke container default entrypoint (make it an option?) with the constructed command line

### Stage out

1. Execution finishes without error (if error see below)
2. Next step in batch script invokes CLI client with token, input dataset id, and destination dataset id
3. Loop over list constructing payload for dataset creation with metadata in place
    * If organized by 'kind' into folders then set field appropriately
    * Using python-irodsclient or similar, place files in folder for destination dataset ID as they are processed (can be parallelized?)
6. POST to create dataset and associated datum records through 'back door' using token
7. POST to move job to finished state, record log
---
8. Back on the server side handle antecedent and webhook
    * Select all jobs where this one was an antecedent and all antecedents are available, and trigger
    * Hit webhook with notification

#### If execution errors

1. Trap exception / CalledProcessError
2. POST to move job to failed state, record log


## SLURM spy



## OGS spy


## `dap`

```
dap ingest irods://path/to/thing dataset_id
dap ingest /home/me/path/to/thing dataset_id --source --stage --kind --friendly-name --description --mark-all-files science
dap retrieve dataset dataset_id [.]
dap retrieve job_inputs job_id [.]
dap retrieve query '{query: payload}' --from-file ./query.json [.]
dap store /path/to/outputs
dap invoke job_id --strategy=OSG
    - retrieve pipeline to stashcache
    - dap retrieve job_inputs job_id /scratch/foo
    - cd /scratch/foo
    - subprocess call singularity container capturing stdout/stderr
        - stream outputs? somewhere non-durable? something for later
    - dap ingest --as-platform . output_dataset_id
dap execute job_id
    retrieve
    invoke
    store
```
