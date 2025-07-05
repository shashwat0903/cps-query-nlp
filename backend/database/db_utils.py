"""
MongoDB connection utilities with SSL handling for Render deployment
"""

import os
import ssl
import certifi
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

def get_mongodb_client(uri=None):
    """
    Create a MongoDB client with SSL configuration that works well on Render
    """
    if uri is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
    # Check if we're using MongoDB Atlas (SRV record)
    is_atlas = "mongodb+srv://" in uri
    
    try:
        # Configure TLS/SSL options
        client = MongoClient(
            uri,
            ssl=is_atlas,
            ssl_ca_certs=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True
        )
        
        # Test the connection
        client.admin.command('ping')
        print(f"✅ MongoDB connection successful")
        return client
        
    except Exception as e:
        print(f"❌ Failed to connect with standard SSL: {e}")
        
        try:
            # Fallback with less strict SSL for some hosting environments
            client = MongoClient(
                uri,
                ssl=is_atlas,
                ssl_cert_reqs=ssl.CERT_NONE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            client.admin.command('ping')
            print(f"✅ MongoDB connection successful with fallback SSL settings")
            return client
            
        except Exception as e2:
            print(f"❌ Failed to connect with fallback SSL: {e2}")
            raise

def get_async_mongodb_client(uri=None):
    """
    Create an async MongoDB client with SSL configuration that works well on Render
    """
    if uri is None:
        uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        
    # Check if we're using MongoDB Atlas (SRV record)
    is_atlas = "mongodb+srv://" in uri
    
    try:
        # Configure TLS/SSL options
        client = AsyncIOMotorClient(
            uri,
            ssl=is_atlas,
            ssl_ca_certs=certifi.where(),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=10000,
            retryWrites=True
        )
        print(f"✅ Async MongoDB connection created")
        return client
        
    except Exception as e:
        print(f"❌ Failed to create async connection with standard SSL: {e}")
        
        try:
            # Fallback with less strict SSL for some hosting environments
            client = AsyncIOMotorClient(
                uri,
                ssl=is_atlas,
                ssl_cert_reqs=ssl.CERT_NONE,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=10000
            )
            print(f"✅ Async MongoDB connection created with fallback SSL settings")
            return client
            
        except Exception as e2:
            print(f"❌ Failed to create async connection with fallback SSL: {e2}")
            raise
