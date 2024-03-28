FROM python:3.11-slim as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    # Allow statements and log messages to immediately appear
    PYTHONUNBUFFERED=1 \
    # disable a pip version check to reduce run-time & log-spam
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # cache is useless in docker image, so disable to reduce image size
    PIP_NO_CACHE_DIR=1 \
    CUDA_VISIBLE_DEVICES=-1

COPY ./requirements.txt ./requirements.txt

RUN pip3 install --user torch torchvision torchaudio torchtext torchdata --index-url https://download.pytorch.org/whl/cpu
RUN pip3 install --user -r requirements.txt


FROM node:18-alpine as frontend-builder

COPY ./ui/web/frontend /app

RUN cd /app && yarn install && yarn build


FROM djvue/urfu-deployments:pi2-base-cpu as final

WORKDIR /app

COPY . .

# copy only the dependencies installation from the 1st stage image
COPY --from=builder /root/.local /root/.local

COPY --from=frontend-builder /app/dist /app/ui/web/frontend/dist

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/_info

ENTRYPOINT ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000"]