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

