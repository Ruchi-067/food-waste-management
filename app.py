# app.py - Main Streamlit application file
# food_waste_app.py
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px

# Initialize database
def init_db():
    conn = sqlite3.connect('c:\\Users\\ruchi\\OneDrive\\Desktop\\streamlit_app\\food_waste.db')
    c = conn.cursor()
    
    # Create tables if they don't exist
    c.execute('''CREATE TABLE IF NOT EXISTS donations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donor_name TEXT NOT NULL,
                food_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                units TEXT NOT NULL,
                expiry_date TEXT NOT NULL,
                location TEXT NOT NULL,
                contact_email TEXT NOT NULL,
                status TEXT DEFAULT 'Available',
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                donation_id INTEGER NOT NULL,
                claimer_name TEXT NOT NULL,
                claimer_contact TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(donation_id) REFERENCES donations(id))''')
    
    conn.commit()
    return conn

conn = init_db()

# Custom CSS styling
st.markdown("""
<style>
    .card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #4CAF50;
    }
    .available { color: #4CAF50; }
    .claimed { color: #FF5722; }
    .expired { color: #9E9E9E; }
    .urgent { background-color: #FFF3E0; }
</style>
""", unsafe_allow_html=True)

# Session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'view' not in st.session_state:
    st.session_state.view = 'list'

# Data functions
def add_donation(data):
    """Add new food donation to database"""
    c = conn.cursor()
    c.execute('''INSERT INTO donations (
                donor_name, food_type, quantity, units, 
                expiry_date, location, contact_email)
                VALUES (?, ?, ?, ?, ?, ?, ?)''', data)
    conn.commit()

def get_donations(filters={}):
    """Get donations with optional filters"""
    query = "SELECT * FROM donations WHERE 1=1"
    params = []
    
    if filters.get('food_type') and filters['food_type'] != 'All':
        query += " AND food_type = ?"
        params.append(filters['food_type'])
    if filters.get('location') and filters['location'] != 'All':
        query += " AND location LIKE ?"
        params.append(f'%{filters["location"]}%')
    if filters.get('donor') and filters['donor'] != 'All':
        query += " AND donor_name = ?"
        params.append(filters['donor'])
    if filters.get('status') and filters['status'] != 'All':
        query += " AND status = ?"
        params.append(filters['status'])
    
    query += " ORDER BY expiry_date ASC"
    return pd.read_sql(query, conn, params=params)

def claim_donation(donation_id, claimer_info):
    """Claim a food donation"""
    c = conn.cursor()
    
    # Add claim record
    c.execute('''INSERT INTO claims (donation_id, claimer_name, claimer_contact)
                 VALUES (?, ?, ?)''', 
              (donation_id, claimer_info['name'], claimer_info['contact']))
    
    # Update donation status
    c.execute('''UPDATE donations SET status = 'Claimed' 
                 WHERE id = ?''', (donation_id,))
    
    conn.commit()

def get_donation_stats():
    """Get statistics about donations"""
    return {
        'available': pd.read_sql("SELECT COUNT(*) FROM donations WHERE status = 'Available'", conn).iloc[0,0],
        'claimed': pd.read_sql("SELECT COUNT(*) FROM donations WHERE status = 'Claimed'", conn).iloc[0,0],
        'total_food': pd.read_sql("SELECT SUM(quantity) FROM donations WHERE status = 'Available'", conn).iloc[0,0] or 0,
        'top_donors': pd.read_sql('''SELECT donor_name, COUNT(*) as count 
                                    FROM donations 
                                    GROUP BY donor_name 
                                    ORDER BY count DESC LIMIT 5''', conn),
        'waste_trend': pd.read_sql('''SELECT strftime('%Y-%m', expiry_date) as month, 
                                      SUM(quantity) as wasted 
                                      FROM donations 
                                      WHERE status = 'Expired' 
                                      GROUP BY month 
                                      ORDER BY month''', conn)
    }

# UI Pages
def login_page():
    """Login/registration page"""
    st.title("🍏 Local Food Waste Management")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                # Simplified auth - in production use proper authentication
                st.session_state.user = {
                    'email': email,
                    'name': email.split('@')[0],
                    'type': 'Donor'  # Default type
                }
                st.session_state.view = 'dashboard'
                st.experimental_rerun()
    
    with tab2:
        with st.form("register_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            user_type = st.selectbox("User Type", ["Donor", "Receiver", "Volunteer"])
            
            if st.form_submit_button("Register"):
                # Simplified registration - in production store securely
                st.session_state.user = {
                    'email': email,
                    'name': name,
                    'type': user_type
                }
                st.session_state.view = 'dashboard'
                st.experimental_rerun()

def dashboard_page():
    """Main dashboard page"""
    st.title(f"Welcome, {st.session_state.user['name']}")
    
    # Navigation menu
    menu_options = ["Browse", "Donate", "Analytics"] if st.session_state.user['type'] == "Donor" else ["Browse", "Analytics"]
    menu_choice = st.sidebar.selectbox("Menu", menu_options)
    
    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.view = 'login'
        st.experimental_rerun()
    
    # Page content
    if menu_choice == "Browse":
        browse_page()
    elif menu_choice == "Donate":
        donate_page()
    elif menu_choice == "Analytics":
        analytics_page()

def browse_page():
    """Page to browse available donations"""
    st.header("Browse Food Donations")
    
    # Filters
    with st.expander("Filter Options"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            food_types = ['All'] + get_distinct_values('food_type')
            food_filter = st.selectbox("Food Type", food_types)
        
        with col2:
            locations = ['All'] + get_distinct_values('location')
            location_filter = st.selectbox("Location", locations)
        
        with col3:
            donors = ['All'] + get_distinct_values('donor_name')
            donor_filter = st.selectbox("Donor", donors)
    
    # Get filtered donations
    donations = get_donations({
        'food_type': food_filter,
        'location': location_filter,
        'donor': donor_filter,
        'status': 'Available'
    })
    
    # Display donations
    if not donations.empty:
        for _, donation in donations.iterrows():
            # Determine card styling
            expiry_date = datetime.strptime(donation['expiry_date'], '%Y-%m-%d').date()
            today = datetime.now().date()
            
            status = "Available"
            card_class = ""
            
            if expiry_date < today:
                status = "Expired"
            elif (expiry_date - today) <= timedelta(days=2):
                status = "Urgent"
                card_class = "urgent"
            
            with st.container():
                st.markdown(f"""
                <div class="card {card_class}">
                    <h3>{donation['food_type']} - {donation['quantity']} {donation['units']}</h3>
                    <p><b>Status:</b> <span class="{status.lower()}">{status}</span></p>
                    <p><b>Location:</b> {donation['location']}</p>
                    <p><b>Expires:</b> {donation['expiry_date']}</p>
                    <p><b>Donor:</b> {donation['donor_name']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Claim button for non-donors
                if st.session_state.user['type'] != "Donor" and status == "Available":
                    with st.expander("Claim this donation"):
                        with st.form(f"claim_form_{donation['id']}"):
                            claimer_name = st.text_input("Your Name")
                            claimer_contact = st.text_input("Contact Info")
                            
                            if st.form_submit_button("Claim"):
                                claim_donation(donation['id'], {
                                    'name': claimer_name,
                                    'contact': claimer_contact
                                })
                                st.success("Donation claimed successfully!")
                                st.experimental_rerun()
    else:
        st.warning("No donations found matching your criteria")

def donate_page():
    """Page to add new donations"""
    st.header("Donate Food")
    
    with st.form("donation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            food_type = st.selectbox("Food Type", 
                                    ["Fruits", "Vegetables", "Dairy", 
                                     "Meat", "Bakery", "Prepared Meals"])
            quantity = st.number_input("Quantity", min_value=0.1, step=0.1)
            units = st.selectbox("Units", ["kg", "lbs", "liters", "items"])
        
        with col2:
            expiry_date = st.date_input("Expiry Date", 
                                      min_value=datetime.now().date())
            location = st.text_input("Pickup Location")
            special_notes = st.text_area("Special Notes")
        
        if st.form_submit_button("Submit Donation"):
            donation_data = (
                st.session_state.user['name'],
                food_type,
                quantity,
                units,
                expiry_date.strftime('%Y-%m-%d'),
                location,
                st.session_state.user['email']
            )
            
            add_donation(donation_data)
            st.success("Thank you for your donation!")

def analytics_page():
    """Page for data analysis and insights"""
    st.header("Analytics Dashboard")
    
    stats = get_donation_stats()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Available Donations", stats['available'])
    col2.metric("Claimed Donations", stats['claimed'])
    col3.metric("Total Food Available", f"{stats['total_food']} kg")
    
    st.subheader("Top Food Donors")
    st.table(stats['top_donors'])
    
    st.subheader("Food Wastage Trend")
    if not stats['waste_trend'].empty:
        fig = px.line(stats['waste_trend'], 
                     x='month', y='wasted',
                     title="Monthly Food Wastage",
                     labels={'wasted': 'Quantity Wasted', 'month': 'Month'})
        st.plotly_chart(fig)
    else:
        st.info("No wastage data available")

# Helper functions
def get_distinct_values(column):
    """Get distinct values from a column"""
    c = conn.cursor()
    c.execute(f"SELECT DISTINCT {column} FROM donations")
    return [row[0] for row in c.fetchall()]

# Main app flow
def main():
    if st.session_state.user is None:
        login_page()
    else:
        dashboard_page()

if __name__ == '__main__':
    st.set_page_config(page_title="Food Waste Management", layout="wide")
    main()
