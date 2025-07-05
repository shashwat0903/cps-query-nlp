#!/usr/bin/env python3
"""
Test MongoDB Atlas connection
"""

import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        # Get connection details
        mongodb_uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("DATABASE_NAME")
        
        print(f"🔍 Testing MongoDB connection...")
        print(f"📝 Database URI: {mongodb_uri[:50]}...")
        print(f"📝 Database Name: {database_name}")
        
        # Create client
        client = MongoClient(mongodb_uri)
        
        # Test connection
        print("🔄 Attempting to connect...")
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[database_name]
        collections = db.list_collection_names()
        print(f"📊 Database '{database_name}' accessible")
        print(f"📋 Collections: {collections}")
        
        # Test creating a collection if none exist
        if not collections:
            print("🆕 Creating test collection...")
            test_collection = db.test_collection
            test_collection.insert_one({"test": "data", "timestamp": "2025-07-05"})
            print("✅ Test collection created successfully")
        
        client.close()
        print("🎉 MongoDB Atlas integration is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

if __name__ == "__main__":
    test_mongodb_connection()
