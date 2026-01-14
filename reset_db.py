#!/usr/bin/env python
"""
Reset database script - removes old database and creates new one with updated schema.
Run this once to fix the classification column issue.
"""

import os
import sys

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

from app import app, db

def reset_database():
    """Drop all tables and recreate them with the new schema"""
    
    db_path = 'instance/dev.db'
    
    print("=" * 70)
    print("DATABASE RESET SCRIPT")
    print("=" * 70)
    print()
    
    # Check if database exists
    if os.path.exists(db_path):
        print(f"Found existing database: {db_path}")
        print("Removing old database...")
        os.remove(db_path)
        print("✓ Old database removed")
    else:
        print(f"No existing database found at {db_path}")
    
    print()
    print("Creating new database with updated schema...")
    
    # Create all tables with the new schema (including classification)
    with app.app_context():
        db.create_all()
        print("✓ New database created successfully")
    
    print()
    print("=" * 70)
    print("DATABASE RESET COMPLETE")
    print("=" * 70)
    print()
    print("The database now includes the 'classification' column.")
    print("You can now submit conferences and they will be classified!")
    print()

if __name__ == '__main__':
    reset_database()
