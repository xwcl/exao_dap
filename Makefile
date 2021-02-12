all: init-python build-assets
init-python: build_assets
	bash -x ./init-python.sh
build-assets:
	bash -x ./build-assets.sh
dev-frontend: build_assets
	cd frontend && yarn run parcel serve frontend/index.html
dev-backend: dev-backend-stop
	docker build . -t exao_dap
	mkdir -p ./state/static/
	rm -rf ./state/static/*
	docker run \
		--name dev_exao_dap \
		-v $(PWD)/state:/var/lib/exao_dap \
		-p 8000:8000 \
		--env-file ./secrets/env \
		--env DAP_DEBUG=1 \
		--detach \
		exao_dap
	docker exec dev_exao_dap env/bin/python manage.py collectstatic
dev-backend-stop:
	docker rm -f dev_exao_dap || true
deploy:
	echo "TODO"

.PHONY: all init-python build-assets serve deploy dev-frontend
