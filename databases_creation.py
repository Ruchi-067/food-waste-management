# database_creation.py
import sqlite3
import pandas as pd

def create_database():
    """Create SQLite database and tables."""
    conn = sqlite3.connect('c:\\Users\\ruchi\\OneDrive\\Desktop\\streamlit_app\\food_waste.db')
    
    # Load cleaned data
    providers = pd.read_csv('providers_clean.csv')
    receivers = pd.read_csv('receivers_clean.csv')
    food_listings = pd.read_csv('food_listings_clean.csv')
    claims = pd.read_csv('claims_clean.csv')

    # Create tables
    providers.to_sql('providers', conn, if_exists='replace', index=False)
    receivers.to_sql('receivers', conn, if_exists='replace', index=False)
    food_listings.to_sql('food_listings', conn, if_exists='replace', index=False)
    claims.to_sql('claims', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()
    print("Database created and tables populated!")

if __name__ == "__main__":
    create_database()
