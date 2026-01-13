# Use an official Node runtime as a parent image
FROM node:20-slim

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (Vite default is 5173)
EXPOSE 5173

# Start the application in development mode
# We use --host to allow external access (essential for Docker)
CMD ["npm", "run", "dev", "--", "--host"]
