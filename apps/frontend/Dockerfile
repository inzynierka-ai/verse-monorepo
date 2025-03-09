# Use the official Node.js image as the base image
FROM node:23

# Set the working directory
WORKDIR /src

# Copy package.json and yarn.lock files
COPY package.json yarn.lock ./

# Install dependencies and vite globally
RUN yarn install --network-timeout 100000 && yarn global add vite

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on
EXPOSE 5173

# Command to run the application
CMD ["yarn", "run", "dev", "--host", "0.0.0.0"]