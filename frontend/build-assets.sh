#!/bin/sh
# note: no bashisms
yarn install
yarn run parcel build --no-content-hash --public-url /static/exao_dap/bundle/ app.scss
