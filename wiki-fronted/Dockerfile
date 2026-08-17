FROM node:latest

WORKDIR /app
COPY package*.json /app/
RUN node -v
RUN npm install

COPY . .
EXPOSE 5173
CMD npm run dev