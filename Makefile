all: init-python build-assets
init-python: build_assets
	bash -x ./init-python.sh
build-assets:
	bash -x ./build-assets.sh
dev-frontend: build_assets
	cd frontend && yarn run parcel serve frontend/index.html
docker-build:
	docker build . -t exao_dap
dev-backend: dev-backend-stop docker-build
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
	docker exec dev_exao_dap env/bin/python manage.py migrate
dev-backend-stop:
	docker rm -f dev_exao_dap || true
deploy: docker-build
	docker tag exao_dap xwcl/exao_dap
	docker push xwcl/exao_dap
	ssh dap.xwcl.science sudo -u exao_dap -i podman pull xwcl/exao_dap
	ssh dap.xwcl.science sudo systemctl restart podman-exao_dap exao_dap-setup

.PHONY: all init-python build-assets serve deploy dev-frontend dev-backend docker-build
