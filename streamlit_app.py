   from pymongo import MongoClient
import json
import streamlit as st
import requests
import datetime

# Initialize session state for login status
if "login_status" not in st.session_state:
    st.session_state["login_status"] = False

# Function to check login credentials
def login_check(un, pwd):
    return st.secrets.get(un) == pwd

# Function for login page
def login():
    login_page = st.container()
    login_page.title("Login")
    with login_page:
        un = st.text_input("Username", placeholder="Enter your username", key="usn")
        pwd = st.text_input("Password", type="password", placeholder="Enter your password", key="pwd")
        if st.button("Login", type="primary"):
            if not un or not pwd:
                st.warning("Username and Password cannot be empty")
            elif login_check(un, pwd):
                st.session_state["login_status"] = True
                st.rerun()  # Use experimental_rerun() to refresh the app state
            else:
                st.error("Invalid Username or Password")

# Function for logout
def logout():
    if st.button("Logout", type="primary"):
        st.session_state.clear()
        st.session_state["login_status"] = False
        st.rerun()

# Function to add expenses
def add_expense():
    if st.session_state['login_status']:
        st.title("Add Expense")
        logout()
        category = st.selectbox(
            "Select the database",
            ("Entertainment", "Food", "Grocery", "Transport", "Others"),
            index=None,
            placeholder="Select Expense Category...",
        )
        amount = st.text_input(label="Enter the amount you spent")
        date = st.date_input("Date of expense", format="YYYY-MM-DD")
        remarks = st.text_input(label="Enter Remarks (optional)")

        if st.button("Add Expense", type="primary"):
            #api_url = "http://127.0.0.1:8000/expense/add_expense/"
            #headers = {"Content-Type": "application/json"}
            data = {"expense_type": category, "amount": amount, "date": datetime.datetime.strptime(date.strftime("%Y-%m-%d"), '%Y-%m-%d'), "remarks": remarks}
            # = requests.post(api_url, headers=headers, json=data)

            #if response.status_code == 200:
                #st.success(response.json().get('message', 'Expense added successfully!'))
            #else:
                #st.error(response.json().get('message', 'Failed to add expense.'))
            
            # MongoDB insertion code (if needed):
            try:
                client = MongoClient(f"mongodb+srv://{st.secrets['username']}:{st.secrets['password']}@clustercurd.elseaha.mongodb.net/?retryWrites=true&w=majority&appName=ClusterCURD")
                my_collection = client['Expenses']['expenses']
                result = my_collection.insert_one(data)
                st.success("Expense added to MongoDB successfully")
            except Exception as e:
                st.error(f"Failed to add expense to MongoDB: {str(e)}")
def show_expenses():
    today = datetime.datetime.now()
    today_year = today.year
    aug_14 = datetime.date(today_year, 8, 14)
    td = datetime.date(today_year, today.month, today.day)
    
    d = st.date_input(
        "Select a date range",
        (aug_14, datetime.date(today_year, today.month, today.day)),
        aug_14,
        td,
        format="MM.DD.YYYY",
    )
    start_date = d[0]  # Start date
    end_date = d[1]
    start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time(), tzinfo=datetime.timezone.utc)
    end_date = datetime.datetime.combine(end_date, datetime.datetime.min.time(), tzinfo=datetime.timezone.utc)
    client = MongoClient(f"mongodb+srv://{st.secrets['username']}:{st.secrets['password']}@clustercurd.elseaha.mongodb.net/retryWrites=true&w=majority&appName=ClusterCURD")
    collection = client['Expenses']['expenses']
    # Aggregation pipeline
    pipeline = [
        {
            '$match': {
                'date': {
                    '$gte': start_date,  # Match documents from start_date
                    '$lte': end_date     # Match documents up to end_date
                }
            }
        },
        {
            '$group': {
                '_id': '$expense_type',  # Group by expense_type
                'total_amount': {
                    '$sum': {
                        '$toDouble': '$amount'  # Convert amount from string to double for summation
                    }
                }
            }
        },
        {
            '$sort': {
                'total_amount': -1  # Sort by total amount descending
            }
        }
    ]
    
    # Execute the query
    result = list(collection.aggregate(pipeline))
    
    # Display results in Streamlit
    st.write("Expense Summary:")
    total_amt = 0
    for doc in result:
        st.write(f"Expense Type: {doc['_id']}, Total Amount: {doc['total_amount']}")
        total_amt += doc['total_amount']
    st.write(f"Total Amount : {total_amt}")
# Main app logic
if not st.session_state["login_status"]:
    login()
else:
    pages = {
        "Add Expenses": add_expense,
        "Show Expenses Summary": show_expenses
    }

    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Display the selected page
    page = pages[selection]
    page()
