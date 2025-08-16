# data_analysis.py
import sqlite3
import pandas as pd

def execute_queries():
    """Execute SQL queries to analyze food donation data."""
    conn = sqlite3.connect('c:\\Users\\ruchi\\OneDrive\\Desktop\\streamlit_app\\food_waste.db')

    # Example queries
    queries = {
        "Providers and Receivers Count": """
            SELECT City, COUNT(DISTINCT Provider_ID) AS Provider_Count, COUNT(DISTINCT Receiver_ID) AS Receiver_Count
            FROM providers
            LEFT JOIN receivers ON providers.City = receivers.City
            GROUP BY City;
        """,
        "Total Food Quantity": """
            SELECT SUM(Quantity) AS Total_Food_Quantity FROM food_listings;
        """,
        "Most Common Food Types": """
            SELECT Food_Type, COUNT(*) AS Count FROM food_listings
            GROUP BY Food_Type ORDER BY Count DESC;
        """,
        # Add more queries as needed...
    }

    results = {}
    for name, query in queries.items():
        results[name] = pd.read_sql_query(query, conn)

    conn.close()
    return results

if __name__ == "__main__":
    results = execute_queries()
    for name, result in results.items():
        print(f"\n{name}:\n", result)
