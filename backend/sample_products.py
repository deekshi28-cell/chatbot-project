#!/usr/bin/env python3
"""
Script to populate MongoDB with sample product data for testing
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database

# Sample product data
SAMPLE_PRODUCTS = [
    {
        "product_name": "iPhone 15",
        "price": 999,
        "description": "Latest Apple smartphone with advanced camera and A17 chip",
        "category": "Electronics"
    },
    {
        "product_name": "MacBook Pro",
        "price": 1999,
        "description": "High-performance laptop with M3 chip for professionals",
        "category": "Electronics"
    },
    {
        "product_name": "AirPods Pro",
        "price": 249,
        "description": "Wireless earbuds with active noise cancellation",
        "category": "Electronics"
    },
    {
        "product_name": "Samsung TV",
        "price": 799,
        "description": "55-inch 4K Smart TV with HDR support",
        "category": "Electronics"
    },
    {
        "product_name": "Nike Shoes",
        "price": 120,
        "description": "Comfortable running shoes with advanced cushioning",
        "category": "Sports"
    }
]

async def populate_products():
    """Populate MongoDB with sample product data"""
    # Load environment variables
    load_dotenv('.env')
    
    # Initialize database
    db = Database()
    await db.connect()
    
    try:
        # Get products collection
        products_collection = db.db["products"]
        
        # Clear existing products
        await products_collection.delete_many({})
        print("Cleared existing products")
        
        # Insert sample products
        result = await products_collection.insert_many(SAMPLE_PRODUCTS)
        print(f"Inserted {len(result.inserted_ids)} products")
        
        # Verify insertion
        count = await products_collection.count_documents({})
        print(f"Total products in database: {count}")
        
        # List all products
        print("\nProducts in database:")
        async for product in products_collection.find({}):
            print(f"- {product['product_name']}: ${product['price']}")
            
    except Exception as e:
        print(f"Error populating products: {e}")
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(populate_products())
