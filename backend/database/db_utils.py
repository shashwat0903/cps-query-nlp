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
        # Simplest connection approach first - let PyMongo handle the URI parsing
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        
        # Test the connection
        client.admin.command('ping')
        print(f"✅ MongoDB connection successful with simple approach")
        return client
        
    except Exception as e:
        print(f"❌ Failed to connect with simple approach: {e}")
        
        try:
            # Try again with explicit TLS settings
            if is_atlas:
                client = MongoClient(
                    uri,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000
                )
            else:
                client = MongoClient(
                    uri,
                    serverSelectionTimeoutMS=5000
                )
                
            # Test the connection
            client.admin.command('ping')
            print(f"✅ MongoDB connection successful with explicit TLS")
            return client
                
        except Exception as e2:
            print(f"❌ Failed to connect with explicit TLS: {e2}")
            
            try:
                # Last attempt with minimal parameters
                client = MongoClient(uri)
                client.admin.command('ping')
                print(f"✅ MongoDB connection successful with minimal parameters")
                return client
            except Exception as e3:
                print(f"❌ All connection attempts failed: {e3}")
                raise
                client = MongoClient(
                    uri,
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
        # Simplest connection approach first
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        print(f"✅ Async MongoDB connection created with simple approach")
        return client
        
    except Exception as e:
        print(f"❌ Failed to create async connection with simple approach: {e}")
        
        try:
            # Try again with explicit TLS settings
            if is_atlas:
                client = AsyncIOMotorClient(
                    uri,
                    tls=True,
                    tlsCAFile=certifi.where(),
                    serverSelectionTimeoutMS=5000
                )
            else:
                client = AsyncIOMotorClient(
                    uri,
                    serverSelectionTimeoutMS=5000
                )
            print(f"✅ Async MongoDB connection created with explicit TLS")
            return client
            
        except Exception as e2:
            print(f"❌ Failed to create async connection with explicit TLS: {e2}")
            
            try:
                # Last attempt with minimal parameters
                client = AsyncIOMotorClient(uri)
                print(f"✅ Async MongoDB connection created with minimal parameters")
                return client
            except Exception as e3:
                print(f"❌ All async connection attempts failed: {e3}")
                raise
            print(f"✅ Async MongoDB connection created with fallback SSL settings")
            return client
            
        except Exception as e2:
            print(f"❌ Failed to create async connection with fallback SSL: {e2}")
            raise
