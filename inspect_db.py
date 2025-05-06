# inspect_db.py
import sqlite3

def inspect_database(db_name='ecommerce.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Check customers table
    cursor.execute("PRAGMA table_info(customers)")
    print("Customers table columns:")
    for column in cursor.fetchall():
        print(column[1])  # column name is at index 1
    
    # Check products table
    cursor.execute("PRAGMA table_info(products)")
    print("\nProducts table columns:")
    for column in cursor.fetchall():
        print(column[1])
    
    conn.close()

if __name__ == "__main__":
    inspect_database()