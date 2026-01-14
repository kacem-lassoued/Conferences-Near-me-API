#!/usr/bin/env python
"""
Safe migration script - adds the classification column to existing database.
This preserves all existing data and only adds the new column.
"""

import os
import sys
import sqlite3

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

def add_classification_column():
    """Add classification column to conferences table"""
    
    db_path = 'instance/dev.db'
    
    print("=" * 70)
    print("SAFE DATABASE MIGRATION - ADD CLASSIFICATION COLUMN")
    print("=" * 70)
    print()
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found at {db_path}")
        print("Cannot migrate non-existent database.")
        return False
    
    print(f"Database found: {db_path}")
    print()
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Checking if 'classification' column already exists...")
        
        # Get table info
        cursor.execute("PRAGMA table_info(conferences)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        if 'classification' in column_names:
            print("✓ Column 'classification' already exists!")
            print()
            print("No migration needed.")
            conn.close()
            return True
        
        print("✗ Column 'classification' not found")
        print()
        print("Adding 'classification' column...")
        
        # Add the column
        cursor.execute("ALTER TABLE conferences ADD COLUMN classification JSON")
        conn.commit()
        
        print("✓ Column added successfully!")
        print()
        
        # Verify it was added
        cursor.execute("PRAGMA table_info(conferences)")
        columns = cursor.fetchall()
        print("Updated conferences table columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == '__main__':
    print()
    success = add_classification_column()
    print()
    print("=" * 70)
    if success:
        print("MIGRATION COMPLETE - All data preserved!")
    else:
        print("MIGRATION FAILED")
    print("=" * 70)
    print()
