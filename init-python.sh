#!/usr/bin/env bash
set -eo pipefail
if [[ ! -d ./env ]]; then python -m venv ./env; fi
if ! ./env/bin/pip freeze | grep irods_fsspec; then
    git clone https://github.com/xwcl/irods_fsspec.git ./env/irods_fsspec
    ./env/bin/pip install -e ./env/irods_fsspec
fi
if ! ./env/bin/pip freeze | grep exao_dap_client; then
    git clone https://github.com/xwcl/exao_dap_client.git ./env/exao_dap_client
    ./env/bin/pip install -e ./env/exao_dap_client
fi
./env/bin/pip install -e .[dev]
if [[ ! -e ./exao_dap/settings.py ]]; then cp ./exao_dap/settings.py.example ./exao_dap/settings.py; fi
