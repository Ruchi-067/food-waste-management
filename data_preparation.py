import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import os

def load_and_clean_data():
    """Load and clean the food donation datasets"""
    try:
        print("=== Local Food Wastage Management System ===")
        print("Loading datasets...")
        
        # Check if CSV files exist
        csv_files = ['providers_data.csv', 'receivers_data.csv', 'food_listings_data.csv', 'claims_data.csv']
        for file in csv_files:
            if not os.path.exists(file):
                print(f"Warning: {file} not found. Creating sample data...")
                create_sample_data()
                break
        
        # Load all CSV files
        providers = pd.read_csv('providers_data.csv')
        receivers = pd.read_csv('receivers_data.csv')
        food_listings = pd.read_csv('food_listings_data.csv')
        claims = pd.read_csv('claims_data.csv')

        print(f"✓ Providers loaded: {providers.shape[0]} records")
        print(f"✓ Receivers loaded: {receivers.shape[0]} records")
        print(f"✓ Food listings loaded: {food_listings.shape[0]} records")
        print(f"✓ Claims loaded: {claims.shape[0]} records")

        # Data Cleaning Steps
        print("\nPerforming data cleaning...")

        # 1. Remove exact duplicates
        providers = providers.drop_duplicates()
        receivers = receivers.drop_duplicates()
        food_listings = food_listings.drop_duplicates()
        claims = claims.drop_duplicates()

        # 2. Handle missing values in providers
        if 'Contact' in providers.columns:
            providers['Contact'] = providers['Contact'].fillna('Not Provided')
        if 'Address' in providers.columns:
            providers['Address'] = providers['Address'].fillna('Address Not Available')
        
        # 3. Handle missing values in receivers
        if 'Contact' in receivers.columns:
            receivers['Contact'] = receivers['Contact'].fillna('Not Provided')
        
        # 4. Clean and validate numeric fields in food_listings
        if 'Quantity' in food_listings.columns:
            food_listings['Quantity'] = pd.to_numeric(food_listings['Quantity'], errors='coerce')
            food_listings['Quantity'] = food_listings['Quantity'].fillna(0).astype(int)
        
        # 5. Clean text fields - standardize naming
        text_columns_providers = ['Name', 'Type', 'City']
        for col in text_columns_providers:
            if col in providers.columns:
                providers[col] = providers[col].astype(str).str.strip().str.title()
        
        text_columns_receivers = ['Name', 'Type', 'City']
        for col in text_columns_receivers:
            if col in receivers.columns:
                receivers[col] = receivers[col].astype(str).str.strip().str.title()
                
        text_columns_food = ['Food_Name', 'Provider_Type', 'Location', 'Food_Type', 'Meal_Type']
        for col in text_columns_food:
            if col in food_listings.columns:
                food_listings[col] = food_listings[col].astype(str).str.strip().str.title()
            
        # 6. Validate and clean food type and meal type
        if 'Food_Type' in food_listings.columns:
            valid_food_types = ['Vegetarian', 'Non-Vegetarian', 'Vegan', 'Mixed']
            food_listings['Food_Type'] = food_listings['Food_Type'].apply(
                lambda x: x if x in valid_food_types else 'Mixed')
            
        if 'Meal_Type' in food_listings.columns:
            valid_meal_types = ['Breakfast', 'Lunch', 'Dinner', 'Snacks']
            food_listings['Meal_Type'] = food_listings['Meal_Type'].apply(
                lambda x: x if x in valid_meal_types else 'Snacks')
            
        # 7. Clean claims data
        if 'Status' in claims.columns:
            claims['Status'] = claims['Status'].astype(str).str.strip().str.capitalize()
            valid_statuses = ['Pending', 'Completed', 'Cancelled', 'Rejected']
            claims['Status'] = claims['Status'].apply(
                lambda x: x if x in valid_statuses else 'Pending')
            
        # 8. Convert dates to datetime objects
        if 'Expiry_Date' in food_listings.columns:
            food_listings['Expiry_Date'] = pd.to_datetime(
                food_listings['Expiry_Date'], errors='coerce')
        
        if 'Timestamp' in claims.columns:
            claims['Timestamp'] = pd.to_datetime(
                claims['Timestamp'], errors='coerce')

        # Final validation and summary
        print("\n=== Data Cleaning Summary ===")
        print(f"Providers - Records: {len(providers)}, Missing values: {providers.isna().sum().sum()}")
        print(f"Receivers - Records: {len(receivers)}, Missing values: {receivers.isna().sum().sum()}")
        print(f"Food Listings - Records: {len(food_listings)}, Missing values: {food_listings.isna().sum().sum()}")
        print(f"Claims - Records: {len(claims)}, Missing values: {claims.isna().sum().sum()}")

        # Display sample data
        print("\n=== Sample Data Preview ===")
        print("Providers (first 3 records):")
        print(providers.head(3))
        print("\nFood Listings (first 3 records):")
        print(food_listings.head(3))

        # Return cleaned data
        return providers, receivers, food_listings, claims

    except Exception as e:
        print(f"Error during data preparation: {e}")
        print("Creating sample data for demonstration...")
        create_sample_data()
        return load_and_clean_data()

def create_sample_data():
    """Create sample CSV files for demonstration"""
    print("Creating sample data files...")
    
    # Sample Providers Data
    providers_data = {
        'Provider_ID': [1, 2, 3, 4, 5],
        'Name': ['Fresh Foods Restaurant', 'Green Grocery Store', 'City Supermarket', 'Healthy Cafe', 'Metro Food Store'],
        'Type': ['Restaurant', 'Grocery Store', 'Supermarket', 'Restaurant', 'Grocery Store'],
        'Address': ['123 Main St', '456 Oak Ave', '789 Pine Rd', '321 Elm St', '654 Maple Dr'],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
        'Contact': ['555-0101', '555-0102', '555-0103', '555-0104', '555-0105']
    }
    
    # Sample Receivers Data
    receivers_data = {
        'Receiver_ID': [1, 2, 3, 4, 5],
        'Name': ['Hope Foundation', 'Community Kitchen', 'Food Bank Central', 'Helping Hands NGO', 'Meal Share Program'],
        'Type': ['NGO', 'Community Center', 'Food Bank', 'NGO', 'Community Center'],
        'City': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'],
        'Contact': ['555-0201', '555-0202', '555-0203', '555-0204', '555-0205']
    }
    
    # Sample Food Listings Data
    food_listings_data = {
        'Food_ID': [1, 2, 3, 4, 5, 6, 7, 8],
        'Food_Name': ['Fresh Sandwiches', 'Organic Vegetables', 'Bakery Items', 'Cooked Rice', 'Fresh Fruits', 'Pasta Meals', 'Dairy Products', 'Snack Items'],
        'Quantity': [20, 15, 30, 25, 40, 18, 12, 35],
        'Expiry_Date': ['2024-01-15', '2024-01-16', '2024-01-14', '2024-01-15', '2024-01-17', '2024-01-16', '2024-01-15', '2024-01-18'],
        'Provider_ID': [1, 2, 3, 4, 5, 1, 2, 3],
        'Provider_Type': ['Restaurant', 'Grocery Store', 'Supermarket', 'Restaurant', 'Grocery Store', 'Restaurant', 'Grocery Store', 'Supermarket'],
        'Location': ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'New York', 'Los Angeles', 'Chicago'],
        'Food_Type': ['Non-Vegetarian', 'Vegetarian', 'Vegetarian', 'Vegetarian', 'Vegan', 'Vegetarian', 'Vegetarian', 'Mixed'],
        'Meal_Type': ['Lunch', 'Dinner', 'Breakfast', 'Lunch', 'Snacks', 'Dinner', 'Breakfast', 'Snacks']
    }
    
    # Sample Claims Data
    claims_data = {
        'Claim_ID': [1, 2, 3, 4, 5, 6],
        'Food_ID': [1, 2, 3, 4, 5, 6],
        'Receiver_ID': [1, 2, 3, 4, 5, 1],
        'Status': ['Completed', 'Pending', 'Completed', 'Cancelled', 'Pending', 'Completed'],
        'Timestamp': ['2024-01-10 10:30:00', '2024-01-11 14:15:00', '2024-01-12 09:45:00', '2024-01-13 16:20:00', '2024-01-14 11:10:00', '2024-01-15 13:30:00']
    }
    
    # Create DataFrames and save to CSV
    pd.DataFrame(providers_data).to_csv('providers_data.csv', index=False)
    pd.DataFrame(receivers_data).to_csv('receivers_data.csv', index=False)
    pd.DataFrame(food_listings_data).to_csv('food_listings_data.csv', index=False)
    pd.DataFrame(claims_data).to_csv('claims_data.csv', index=False)
    
    print("✓ Sample CSV files created successfully!")

def save_to_database(providers, receivers, food_listings, claims):
    """Save cleaned data to SQLite database"""
    try:
        conn = sqlite3.connect('food_donations.db')
        
        # Save dataframes to database
        providers.to_sql('providers', conn, if_exists='replace', index=False)
        receivers.to_sql('receivers', conn, if_exists='replace', index=False)
        food_listings.to_sql('food_listings', conn, if_exists='replace', index=False)
        claims.to_sql('claims', conn, if_exists='replace', index=False)
        
        conn.commit()
        conn.close()
        
        print("✓ Data successfully saved to SQLite database!")
        
    except Exception as e:
        print(f"Error saving to database: {e}")

if __name__ == "__main__":
    # Execute the data preparation when run directly
    providers_clean, receivers_clean, food_listings_clean, claims_clean = load_and_clean_data()
    
    # Save cleaned data to new CSVs
    providers_clean.to_csv('providers_clean.csv', index=False)
    receivers_clean.to_csv('receivers_clean.csv', index=False)
    food_listings_clean.to_csv('food_listings_clean.csv', index=False)
    claims_clean.to_csv('claims_clean.csv', index=False)
    
    # Save to database
    save_to_database(providers_clean, receivers_clean, food_listings_clean, claims_clean)
    
    print("\n=== Data Preparation Complete! ===")
    print("Files created:")
    print("- providers_clean.csv")
    print("- receivers_clean.csv") 
    print("- food_listings_clean.csv")
    print("- claims_clean.csv")
    print("- food_donations.db (SQLite database)")

