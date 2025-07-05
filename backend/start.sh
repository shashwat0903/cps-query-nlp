#!/bin/bash
# Start the FastAPI server
cd /opt/render/project/src/
python -m uvicorn server:app --host 0.0.0.0 --port $PORT
