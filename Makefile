all: yarn_install python_install exao_dap/static/bundle/app.css
python_install:
	if [[ ! -d ./env ]]; then python -m venv ./env; fi
	./env/bin/pip install -e .
yarn_install:
	yarn install
exao_dap/static/bundle/app.css:
	yarn run parcel build --no-content-hash -d ./exao_dap/static/bundle/ --public-url /static/bundle/ frontend/app.scss
serve: yarn_install
	yarn run parcel serve frontend/index.html
deploy: yarn_install exao_dap/static/bundle/app.css python_install
	echo "TODO"

.PHONY: all python_install yarn_install serve deploy
