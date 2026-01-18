import os
import sys
from database import init_db, engine
from sqlalchemy import inspect

def check_and_init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    print(f"Existing tables: {existing_tables}")
    
    init_db()
    
    inspector = inspect(engine)
    new_tables = inspector.get_table_names()
    
    print(f"Tables after init: {new_tables}")
    print("Database initialized successfully!")

if __name__ == "__main__":
    check_and_init_db()
