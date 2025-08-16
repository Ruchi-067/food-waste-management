import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("c:\\Users\\ruchi\\OneDrive\\Desktop\\streamlit_app\\food_donations.db")
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS providers (
        Provider_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        Address TEXT NOT NULL,
        City TEXT NOT NULL,
        Contact TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID INTEGER PRIMARY KEY,
        Name TEXT NOT NULL,
        Type TEXT NOT NULL,
        City TEXT NOT NULL,
        Contact TEXT NOT NULL)''')

    c.execute('''CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY,
        Food_Name TEXT NOT NULL,
        Quantity INTEGER NOT NULL,
        Expiry_Date DATE NOT NULL,
        Provider_ID INTEGER NOT NULL,
        Provider_Type TEXT NOT NULL,
        Location TEXT NOT NULL,
        Food_Type TEXT NOT NULL,
        Meal_Type TEXT NOT NULL,
        FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID))''')

    c.execute('''CREATE TABLE IF NOT EXISTS claims (
        Claim_ID INTEGER PRIMARY KEY,
        Food_ID INTEGER NOT NULL,
        Receiver_ID INTEGER NOT NULL,
        Status TEXT NOT NULL,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (Food_ID) REFERENCES food_listings(Food_ID),
        FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID))''')
    
    conn.commit()
    return conn

conn = init_db()

# Load data from CSV files
def load_data():
    providers_df = pd.read_csv("providers_data.csv")
    receivers_df = pd.read_csv("receivers_data.csv")
    food_listings_df = pd.read_csv("food_listings_data.csv")
    claims_df = pd.read_csv("claims_data.csv")

    # Insert data into SQL tables
    providers_df.to_sql("providers", conn, if_exists="append", index=False)
    receivers_df.to_sql("receivers", conn, if_exists="append", index=False)
    food_listings_df.to_sql("food_listings", conn, if_exists="append", index=False)
    claims_df.to_sql("claims", conn, if_exists="append", index=False)

load_data()

# Streamlit App Layout
st.set_page_config(page_title="Food Waste Management", layout="wide")

st.title("🍏 Food Waste Management System")

# Sidebar Filters
st.sidebar.title("Filters")
selected_city = st.sidebar.selectbox("Select City", ["All"] + list(pd.read_sql("SELECT DISTINCT City FROM providers", conn)["City"]))
selected_provider_type = st.sidebar.selectbox("Select Provider Type", ["All"] + list(pd.read_sql("SELECT DISTINCT Type FROM providers", conn)["Type"]))
selected_food_type = st.sidebar.selectbox("Select Food Type", ["All"] + list(pd.read_sql("SELECT DISTINCT Food_Type FROM food_listings", conn)["Food_Type"]))

# Main Dashboard
st.header("Food Donations Overview")

# SQL Queries
query = "SELECT * FROM food_listings WHERE 1=1"
if selected_city != "All":
    query += f" AND Location = '{selected_city}'"
if selected_provider_type != "All":
    query += f" AND Provider_Type = '{selected_provider_type}'"
if selected_food_type != "All":
    query += f" AND Food_Type = '{selected_food_type}'"

food_data = pd.read_sql(query, conn)

# Display Food Listings
st.dataframe(food_data)

# EDA Section
st.header("Exploratory Data Analysis")

# Total Quantity of Food Available
total_quantity = food_data['Quantity'].sum()
st.metric("Total Quantity of Food Available", f"{total_quantity} items")

# Food Type Distribution
fig = px.pie(food_data, names='Food_Type', values='Quantity', title='Food Type Distribution')
st.plotly_chart(fig)

# Claims Overview
st.header("Claims Overview")
claims_data = pd.read_sql("SELECT * FROM claims", conn)

# Claims by Food Item
claims_by_food = claims_data.groupby('Food_ID').size().reset_index(name='Claim_Count')
food_claims = food_data.merge(claims_by_food, on='Food_ID', how='left').fillna(0)

# Display Claims
st.dataframe(food_claims[['Food_Name', 'Claim_Count']])

# Contact Information
st.header("Contact Information")
if st.button("Show Providers Contact Info"):
    providers_info = pd.read_sql("SELECT * FROM providers", conn)
    st.dataframe(providers_info[['Name', 'Contact', 'City']])

# Footer
st.sidebar.markdown("---")
st.sidebar.info("This application helps manage food donations and reduce waste.")
