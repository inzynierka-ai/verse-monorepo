FROM node:22-alpine

WORKDIR /app

COPY package.json yarn.lock ./

RUN yarn install

EXPOSE 5173

CMD ["yarn", "dev", "--host", "0.0.0.0"]
