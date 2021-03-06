all: init-python build-assets
init-python: build-assets
	bash -x ./init-python.sh
build-assets:
	cd frontend/ && bash -x ./build-assets.sh
	cp -R frontend/dist/* ./exao_dap/static/exao_dap/bundle/
dev-frontend: build-assets
	cd frontend && yarn run parcel serve index.html
runserver:
	./manage.py runserver_plus --nopin
docker-build:
	docker build . -t exao_dap
docker-build-force:
	docker build --no-cache . -t exao_dap
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
deploy: docker-build-force
	docker tag exao_dap xwcl/exao_dap
	docker push xwcl/exao_dap
	ssh dap.xwcl.science sudo -u exao_dap -i podman pull xwcl/exao_dap
	ssh dap.xwcl.science sudo systemctl restart podman-exao_dap exao_dap-setup exao_dap-qcluster

.PHONY: all init-python build-assets serve deploy dev-frontend dev-backend docker-build
