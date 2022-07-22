# Declare the base image
FROM node:lts-alpine3.14

RUN mkdir /frontend

COPY package*.json /frontend

WORKDIR /frontend

RUN npm ci

COPY . .

EXPOSE 8080

CMD ["npm", "run", "dev"]

COPY . .
