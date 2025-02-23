import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.express as px

# Initialize Firebase
if "firebase" in st.secrets:
    firebase_credentials = st.secrets["firebase"]
    cred_dict = json.loads(firebase_credentials)
    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    st.error("Firebase credentials not found in Streamlit secrets.")
    st.stop()

# Fetch data from Firestore
def fetch_data(collection_name):
    try:
        docs = db.collection(collection_name).stream()
        data = [{"id": doc.id, **doc.to_dict()} for doc in docs]
        return data if data else None
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

# Delete record
def delete_record(collection_name, doc_id):
    try:
        db.collection(collection_name).document(doc_id).delete()
        st.success("Record deleted successfully.")
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting record: {e}")

# Display Data
def display_data(collection_name):
    data = fetch_data(collection_name)
    if data:
        df = pd.DataFrame(data)

        # Convert date columns if they exist
        date_columns = ['sale_date', 'stocked_date', 'debtor_date']
        for date_col in date_columns:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

        st.dataframe(df)

        # Add delete buttons
        for index, row in df.iterrows():
            if st.button(f"Delete {row['id']}", key=f"delete_{row['id']}"):
                delete_record(collection_name, row['id'])
    else:
        st.write("No data available.")

# Streamlit App UI
st.title('Jusmel Beauty Haven')
st.write('Manage your sales, inventory, and debtors efficiently.')

# Sidebar Navigation
menu = st.sidebar.radio("Menu", ["Inventory", "Sales", "Debtors", "Summary", "Reports"])

# Inventory Management
if menu == "Inventory":
    st.subheader("Inventory Management")
    with st.form("inventory_form"):
        data = {
            "stocked_date": st.date_input("Date Stocked", datetime.today()).strftime('%Y-%m-%d'),
            "source": st.text_input("Source"),
            "perfume_name": st.text_input("Perfume Name"),
            "amount_paid": st.number_input("Amount Paid", min_value=0.0, step=0.01),
            "quantity": st.number_input("Quantity", min_value=1, step=1),
            "gender": st.selectbox("Gender", ["Masculine", "Feminine", "Unisex"]),
            "description": st.text_area("Description"),
            "comments": st.text_area("Comments")
        }
        if st.form_submit_button("Add to Inventory"):
            db.collection('inventory').add(data)
            st.success("Item added successfully")
            st.rerun()
    display_data('inventory')

# Sales Tracking
elif menu == "Sales":
    st.subheader("Sales Tracking")
    with st.form("sales_form"):
        sale_data = {
            "sale_date": st.date_input("Date Sold", datetime.today()).strftime('%Y-%m-%d'),
            "buyer_name": st.text_input("Buyer Name"),
            "perfume_name": st.text_input("Perfume Name"),
            "sale_amount": st.number_input("Amount", min_value=0.0, step=0.01),
            "sale_quantity": st.number_input("Quantity Sold", min_value=1, step=1),
            "sale_comments": st.text_area("Comments")
        }
        if st.form_submit_button("Record Sale"):
            db.collection('sales').add(sale_data)
            st.success("Sale recorded successfully")
            st.rerun()
    display_data('sales')

# Debtors Management
elif menu == "Debtors":
    st.subheader("Debtors Management")
    with st.form("debtors_form"):
        debtor_data = {
            "debtor_name": st.text_input("Debtor Name"),
            "debtor_phone": st.text_input("Telephone Number"),
            "debtor_date": st.date_input("Date", datetime.today()).strftime('%Y-%m-%d'),
            "debtor_amount": st.number_input("Amount", min_value=0.0, step=0.01),
            "debtor_comments": st.text_area("Comments")
        }
        if st.form_submit_button("Add Debtor"):
            db.collection('debtors').add(debtor_data)
            st.success("Debtor added successfully")
            st.rerun()
    display_data('debtors')

# Weekly Summary
elif menu == "Summary":
    st.subheader("Weekly Summary")
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.now())
    
    sales_data = fetch_data('sales')
    if sales_data:
        df = pd.DataFrame(sales_data)
        if 'sale_date' in df.columns:
            df['sale_date'] = pd.to_datetime(df['sale_date'], errors='coerce')
            df = df.dropna(subset=['sale_date'])
            df_filtered = df[(df['sale_date'] >= start_date) & (df['sale_date'] <= end_date)]
            if not df_filtered.empty:
                fig = px.bar(df_filtered, x='sale_date', y='sale_amount', title='Weekly Sales Summary')
                st.plotly_chart(fig)
            else:
                st.write("No sales data for selected period.")
        else:
            st.write("No sales date available.")
    else:
        st.write("No sales data available.")

# Reports
elif menu == "Reports":
    st.subheader("Reports")
    report_type = st.selectbox("Select Report Type", ["Inventory", "Sales", "Debtors"])
    display_data(report_type.lower())

