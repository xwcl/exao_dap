all: styles
yarn_install:
	yarn install
styles: yarn_install
	yarn run parcel build --no-content-hash -d ./exao_dap/static/bundle/ --public-url /static/bundle/ frontend/app.scss
serve: yarn_install
	yarn run parcel serve frontend/index.html
.PHONY: all styles
