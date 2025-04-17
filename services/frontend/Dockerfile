FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json .
RUN npm install

# Copy source
COPY public ./public
COPY src ./src

# Start dev server
CMD ["npm", "start"]
