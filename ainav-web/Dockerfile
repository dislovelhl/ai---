FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

# In development, we use npm run dev
CMD ["npm", "run", "dev"]
