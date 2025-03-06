# Stage 1: Build the application
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy dependency manifests
COPY package.json package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the source code
COPY . .

# Build the Next.js app
RUN npm run build

# Stage 2: Prepare the production image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy dependency manifests for production install
COPY package.json package-lock.json* ./

# Install only production dependencies
RUN npm install --production

# Copy build artifacts and public assets from the builder stage
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public

# Expose the port Next.js runs on (default 3000)
EXPOSE 3000

# Start the Next.js application
CMD ["npm", "start"]
