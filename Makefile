all: yarn_install python_install styles
python_install:
	if [[ ! -d ./env ]]; then python -m venv ./env; fi
	./env/bin/pip install -e .
	if [[ ! -e ./exao_dap/settings.py ]]; then cp ./exao_dap/settings.py.example ./exao_dap/settings.py; fi
	./env/bin/python manage.py migrate
yarn_install:
	yarn install
styles:
	yarn run parcel build --no-content-hash -d ./exao_dap/static/bundle/ --public-url /static/bundle/ frontend/app.scss
serve: yarn_install
	yarn run parcel serve frontend/index.html
deploy: yarn_install exao_dap/static/bundle/app.css python_install
	echo "TODO"

.PHONY: all python_install yarn_install styles serve deploy
