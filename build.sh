#!/bin/bash

# Render deployment build script
# This script installs dependencies and builds the React frontend

set -e  # Exit on any error

echo "Starting build process..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Navigate to frontend directory and install Node.js dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install

# Build React frontend for production (treat warnings as warnings, not errors)
echo "Building React frontend..."
CI=false npm run build

# Return to root directory
cd ..

# Verify that the build was successful
if [ -d "frontend/build" ]; then
    echo "React build completed successfully"
    echo "Build directory contents:"
    ls -la frontend/build/
else
    echo "ERROR: React build failed - build directory not found"
    exit 1
fi

# Verify that model files are accessible
echo "Verifying model files..."
if [ -d "model" ]; then
    echo "Model directory found:"
    ls -la model/
else
    echo "WARNING: Model directory not found"
fi

echo "Build process completed successfully!"