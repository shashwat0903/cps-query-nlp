#!/usr/bin/env python3
"""
Run the FastAPI server directly
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Starting FastAPI server...")
    print("📊 MongoDB Atlas integration enabled")
    print("🔗 Server will be available at: http://localhost:5000")
    print("📚 API documentation at: http://localhost:5000/docs")
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )
