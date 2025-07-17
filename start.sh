#!/bin/bash

# Render deployment start script
# This script launches the Flask app with proper port configuration

set -e  # Exit on any error

echo "Starting Flask application..."

# Set environment variables for production
export FLASK_ENV=production
export PYTHONPATH="${PYTHONPATH}:."

# Verify that the React build exists
if [ ! -d "frontend/build" ]; then
    echo "ERROR: React build directory not found. Make sure build.sh was run successfully."
    exit 1
fi

# Verify that model files exist
if [ ! -d "model" ]; then
    echo "WARNING: Model directory not found. Application may not function correctly."
fi

# Check if PORT environment variable is set (Render provides this)
if [ -z "$PORT" ]; then
    echo "WARNING: PORT environment variable not set. Using default port 5050."
    export PORT=5050
else
    echo "Using PORT from environment: $PORT"
fi

# Start the Flask application
echo "Launching Flask app on port $PORT..."
python app.py