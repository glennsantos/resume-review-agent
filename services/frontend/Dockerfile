FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json .
RUN npm install

# Copy source
COPY public ./public
COPY src ./src

# Start dev server
ENV HOST=0.0.0.0
ENV PORT=4000
EXPOSE 4000
CMD ["npm", "start"]
