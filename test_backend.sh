#!/bin/bash
# Test script to verify backend functionality before deployment

echo "Testing backend functionality..."
cd backend

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "Python not found. Please install Python 3.8 or higher."
    exit 1
fi

# Check if the required packages are installed
if ! pip show fastapi uvicorn python-dotenv > /dev/null; then
    echo "Installing required packages..."
    pip install -r requirements.txt
fi

# Run the server for testing
echo "Starting server for testing..."
python -m uvicorn server:app --host 127.0.0.1 --port 8080 &
SERVER_PID=$!

# Wait for the server to start
sleep 3

# Test the API
echo "Testing API..."
curl -s http://localhost:8080/ | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "✅ Backend health check passed"
else
    echo "❌ Backend health check failed"
    kill $SERVER_PID
    exit 1
fi

# Kill the server
kill $SERVER_PID

echo "Backend tests completed successfully!"
