FROM node:18-alpine as frontend-builder

COPY ./ui/web/frontend /app

RUN cd /app && yarn install && yarn build


FROM djvue/urfu-deployments:pi2-base-cpu-tiny as final

WORKDIR /app

COPY . .

RUN apt install libsox-dev
RUN pip3 install -r requirements.txt

COPY --from=frontend-builder /app/dist /app/ui/web/frontend/dist

EXPOSE 8000

HEALTHCHECK CMD curl --fail http://localhost:8000/_info

ENTRYPOINT ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "8000"]