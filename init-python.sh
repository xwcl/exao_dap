#!/usr/bin/env bash
set -eo pipefail
if [[ ! -d ./env ]]; then python -m venv ./env; fi
if ! ./env/bin/pip freeze | grep irods_fsspec; then
    git clone https://github.com/xwcl/irods_fsspec.git ./env/irods_fsspec
    ./env/bin/pip install -e ./env/irods_fsspec
fi
./env/bin/pip install -e .
if [[ ! -e ./exao_dap/settings.py ]]; then cp ./exao_dap/settings.py.example ./exao_dap/settings.py; fi
