import sqlite3

def create_database():
    # Connect to SQLite database (it will create the database file if it doesn't exist)
    conn = sqlite3.connect('c:\\Users\\ruchi\\OneDrive\\Desktop\\streamlit_app\\food_donations.db')
    
    # Create a cursor object
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS providers (
            Provider_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Type TEXT NOT NULL,
            Address TEXT,
            City TEXT,
            Contact TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS receivers (
            Receiver_ID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Type TEXT NOT NULL,
            City TEXT,
            Contact TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_listings (
            Food_ID INTEGER PRIMARY KEY,
            Food_Name TEXT NOT NULL,
            Quantity INTEGER NOT NULL,
            Expiry_Date DATE,
            Provider_ID INTEGER,
            Provider_Type TEXT,
            Location TEXT,
            Food_Type TEXT,
            Meal_Type TEXT,
            FOREIGN KEY (Provider_ID) REFERENCES providers (Provider_ID)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            Claim_ID INTEGER PRIMARY KEY,
            Food_ID INTEGER,
            Receiver_ID INTEGER,
            Status TEXT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (Food_ID) REFERENCES food_listings (Food_ID),
            FOREIGN KEY (Receiver_ID) REFERENCES receivers (Receiver_ID)
        )
    ''')
    
    # Commit changes and close the connection
    conn.commit()
    conn.close()
    print("Database and tables created successfully!")

if __name__ == "__main__":
    create_database()
