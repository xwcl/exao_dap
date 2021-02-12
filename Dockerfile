FROM node:lts-alpine@sha256:dab92d3da5d881362f46d04cad980ac0f25f4fcf23081f186057288d8e1589a0 as assetBuild
ADD ./frontend /frontend
WORKDIR /frontend
# alpine lacks bash but we're not using bashisms
RUN sh -x ./build-assets.sh
# RUN rm -rf node_modules .cache .parcel-cache yarn-error.log
FROM python:latest@sha256:ca8bd3c91af8b12c2d042ade99f7c8f578a9f80a0dbbd12ed261eeba96dd632f
ADD README.md VERSION init-python.sh manage.py setup.py /exao_dap/
ADD exao_dap /exao_dap/exao_dap
WORKDIR /exao_dap
COPY --from=assetBuild /frontend/dist/ /exao_dap/exao_dap/static/exao_dap/bundle/
# debian has bash but must be invoked by that name
RUN bash -x ./init-python.sh
VOLUME /var/lib/exao_dap
EXPOSE 8000
ENTRYPOINT [ "/exao_dap/env/bin/gunicorn", "exao_dap.wsgi", "--bind", "0.0.0.0:8000" ]
