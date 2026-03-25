import pandas as pd
import streamlit as st
import random
import datetime
from datetime import timedelta
import sqlite3
import hashlib  # Added for Security

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("blood_bank_management_system.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    """Initializes all required tables with correct schemas."""
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT PRIMARY KEY, password TEXT)")
    
    c.execute("""CREATE TABLE IF NOT EXISTS donors (
                DonorID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Age INTEGER, 
                Gender TEXT, BloodGroup TEXT, Contact TEXT, 
                DonatedDate DATE, City TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS recipients (
                ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Age INTEGER, 
                Gender TEXT, BloodGroup TEXT, Contact TEXT, 
                RequestDate DATE, City TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS hospitals (
                HospitalID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, 
                Location TEXT, Contact TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
                UnitID INTEGER PRIMARY KEY AUTOINCREMENT, BloodGroup TEXT, 
                Quantity INTEGER, CollectionDate DATE, 
                ExpiryDate DATE, QualityStatus TEXT)""")
    
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, RecipientID INTEGER, 
                DonorID INTEGER, BloodGroup TEXT, 
                Quantity INTEGER, Date DATE)""")
    conn.commit()

init_db()

# ---------- SECURITY HELPERS ----------
def make_hashes(password):
    """Encodes password to SHA256 hash."""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Checks if the entered password matches the stored hash."""
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# ---------- HELPER FUNCTIONS ----------
def add_user(u, p):
    """Securely adds a user with a hashed password."""
    hashed_p = make_hashes(p)
    try:
        c.execute("INSERT INTO users(username, password) VALUES (?,?)", (u, hashed_p))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(u, p):
    """Verifies user credentials using hashing."""
    c.execute("SELECT password FROM users WHERE username=?", (u,))
    data = c.fetchone()
    if data:
        return check_hashes(p, data[0])
    return False

def delete_record(table, id_column, id_val):
    """Generic function to delete records safely."""
    try:
        c.execute(f"DELETE FROM {table} WHERE {id_column} = ?", (id_val,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False

# ---------- UI CONFIG ----------
st.set_page_config(page_title="Vital Flow", layout="wide", page_icon="🩸")

st.markdown("""
<style>
    .stApp { background-color: #fdfdfd; }
    .stTabs [role="tablist"] { justify-content: space-evenly; }
    .stTabs [role="tab"] { flex: 1; text-align: center; font-weight: bold; font-size: 18px; }
    .main-title { text-align: center; color: #b22222; font-family: 'Trebuchet MS'; }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "login" not in st.session_state:
    st.session_state.login = False

# ---------- LOGIN/SIGNUP PAGE ----------
if not st.session_state.login:
    st.markdown("<h1 class='main-title'>🏥 VitalFlow: Smart Blood Bank</h1>", unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["Login", "Signup"])

    with tab_login:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if login_user(u, p):
                st.session_state.login = True
                st.session_state.user = u
                st.success(f"Welcome back, {u}!")
                st.rerun()
            else:
                st.error("Invalid Username or Password")

    with tab_signup:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account", use_container_width=True):
            if new_u and new_p:
                if add_user(new_u, new_p):
                    st.success("Account created successfully! Please switch to Login tab.")
                else:
                    st.error("Username already exists. Please choose another.")
            else:
                st.warning("Username and Password cannot be empty.")


# ---------- MAIN APP ----------
else:
    st.sidebar.success(f"👋 Logged in as: {st.session_state.user}")
    admin_mode = st.sidebar.toggle("🧑‍⚕️ Admin Dashboard")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.login = False
        st.rerun()

    st.markdown("<h1 class='main-title'>🩸 VitalFlow Management System</h1>", unsafe_allow_html=True)

    if admin_mode:
        t1, t2, t3, t4, t5, t6 = st.tabs(["Home", "Donors", "Requests", "Hospitals", "Inventory", "Transactions"])

        # TAB 1: HOME
        with t1:
            st.subheader("📊 Dashboard Statistics")
            c1, c2, c3 = st.columns(3)
            donors_n = pd.read_sql("SELECT COUNT(*) FROM donors", conn).iloc[0,0]
            req_n = pd.read_sql("SELECT COUNT(*) FROM recipients", conn).iloc[0,0]
            inv_n = pd.read_sql("SELECT SUM(Quantity) FROM inventory", conn).iloc[0,0] or 0
            
            c1.metric("Registered Donors", donors_n)
            c2.metric("Pending Requests", req_n)
            c3.metric("Total Stock (ml)", f"{inv_n}ml")

        # TAB 2: DONORS
        with t2:
            st.subheader("🩸 Donor Database")
            df_d = pd.read_sql("SELECT * FROM donors", conn)
            st.dataframe(df_d, use_container_width=True)
            
            with st.expander("➕ Register New Donor"):
                with st.form("donor_form"):
                    col_a, col_b = st.columns(2)
                    d_name = col_a.text_input("Full Name")
                    d_age = col_a.number_input("Age", 18, 65)
                    d_bg = col_b.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    d_city = col_b.text_input("City")
                    d_contact = col_a.text_input("Contact Number")
                    d_gender = col_b.radio("Gender", ["Male", "Female", "Other"], horizontal=True)
                    if st.form_submit_button("Add Donor"):
                        c.execute("INSERT INTO donors (Name, Age, Gender, BloodGroup, Contact, DonatedDate, City) VALUES (?,?,?,?,?,?,?)",
                                  (d_name, d_age, d_gender, d_bg, d_contact, datetime.date.today(), d_city))
                        conn.commit()
                        st.success("Donor added successfully!")
                        st.rerun()

            with st.expander("🗑️ Remove Donor Record"):
                del_id = st.number_input("Enter Donor ID to Delete", min_value=1, key="del_donor")
                if st.button("Delete Donor", type="primary"):
                    if delete_record("donors", "DonorID", del_id):
                        st.success(f"Donor ID {del_id} deleted.")
                        st.rerun()

        # TAB 3: REQUESTS
        with t3:
            st.subheader("📩 Patient Blood Requests")
            df_r = pd.read_sql("SELECT * FROM recipients", conn)
            if not df_r.empty:
                st.dataframe(df_r, use_container_width=True)
            else:
                st.info("No active blood requests found.")
            
            with st.expander("➕ Add New Request"):
                with st.form("request_form"):
                    col_a, col_b = st.columns(2)
                    r_name = col_a.text_input("Full Name")
                    r_age = col_a.number_input("Age", 18, 65)
                    r_bg = col_b.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    r_city = col_b.text_input("City")
                    r_contact = col_a.text_input("Contact Number")
                    r_gender = col_b.radio("Gender", ["Male", "Female", "Other"], horizontal=True)
                    if st.form_submit_button("Add Request"):
                        c.execute("INSERT INTO recipients (Name, Age, Gender, BloodGroup, Contact, RequestDate, City) VALUES (?,?,?,?,?,?,?)",
                                  (r_name, r_age, r_gender, r_bg, r_contact, datetime.date.today(), r_city))
                        conn.commit()
                        st.success("Request added successfully!")
                        st.rerun()

            with st.expander("🗑️ Remove Request Record"):
                del_id = st.number_input("Enter Request ID to Delete", min_value=1, key="del_req")
                if st.button("Delete Request", type="primary"):
                    if delete_record("recipients", "ID", del_id):
                        st.success(f"Request ID {del_id} deleted.")
                        st.rerun()

        # TAB 4: HOSPITALS
        with t4:
            st.subheader("🏥 Partnered Hospitals")
            df_h = pd.read_sql("SELECT * FROM hospitals", conn)
            st.dataframe(df_h, use_container_width=True)
            
            with st.expander("➕ Register Hospital"):
                with st.form("hosp_form"):
                    h_name = st.text_input("Hospital Name")
                    h_loc = st.text_input("Location/Address")
                    h_con = st.text_input("Emergency Contact")
                    if st.form_submit_button("Register Hospital"):
                        c.execute("INSERT INTO hospitals (Name, Location, Contact) VALUES (?,?,?)", (h_name, h_loc, h_con))
                        conn.commit()
                        st.rerun()

            with st.expander("🗑️ Remove Hospital Record"):
                del_id = st.number_input("Enter Hospital ID to Delete", min_value=1, key="del_hosp")
                if st.button("Delete Hospital", type="primary"):
                    if delete_record("hospitals", "HospitalID", del_id):
                        st.success(f"Hospital ID {del_id} deleted.")
                        st.rerun()

        # TAB 5: INVENTORY
        with t5:
            st.subheader("📦 Inventory Management")
            df_i = pd.read_sql("SELECT * FROM inventory", conn)
            st.dataframe(df_i, use_container_width=True)
            
            with st.expander("➕ Add Stock"):
                with st.form("stock_form"):
                    s_bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    s_qty = st.number_input("Quantity (ml)", 250, 1000, step=50)
                    if st.form_submit_button("Update Inventory"):
                        exp = datetime.date.today() + timedelta(days=35)
                        c.execute("INSERT INTO inventory (BloodGroup, Quantity, CollectionDate, ExpiryDate, QualityStatus) VALUES (?,?,?,?,?)",
                                  (s_bg, s_qty, datetime.date.today(), exp, "Excellent"))
                        conn.commit()
                        st.rerun()

            with st.expander("🗑️ Remove Stock Record"):
                del_id = st.number_input("Enter Unit ID to Delete", min_value=1, key="del_inv")
                if st.button("Delete Stock Item", type="primary"):
                    if delete_record("inventory", "UnitID", del_id):
                        st.success(f"Unit ID {del_id} deleted.")
                        st.rerun()

        # TAB 6: TRANSACTIONS
        with t6:
            st.subheader("💳 Dispatch & Transactions")
            df_t = pd.read_sql("SELECT * FROM transactions", conn)
            st.dataframe(df_t, use_container_width=True)
            
            with st.expander("📝 Record Dispatch"):
                with st.form("trans_form"):
                    t_rid = st.number_input("Recipient ID", min_value=1)
                    t_did = st.number_input("Donor ID (Optional)", min_value=0)
                    t_bg = st.selectbox("Group Dispatched", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    t_qty = st.number_input("Amount (ml)", 100)
                    if st.form_submit_button("Log Transaction"):
                        c.execute("INSERT INTO transactions (RecipientID, DonorID, BloodGroup, Quantity, Date) VALUES (?,?,?,?,?)",
                                  (t_rid, t_did, t_bg, t_qty, datetime.date.today()))
                        conn.commit()
                        st.success("Transaction Recorded.")
                        st.rerun()

            with st.expander("🗑️ Remove Transaction Record"):
                del_id = st.number_input("Enter Transaction ID to Delete", min_value=1, key="del_trans")
                if st.button("Delete Transaction", type="primary"):
                    if delete_record("transactions", "TransactionID", del_id):
                        st.success(f"Transaction ID {del_id} deleted.")
                        st.rerun()

    else:
        st.divider()
# ---------- PUBLIC SEARCH VIEW (UPDATED) ----------
        st.subheader("🔍 Public Dashboard")
        
        c1, c2 = st.columns(2)
        s_bg = c1.selectbox("Filter by Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        s_city = c2.selectbox("Filter by City", ["","Ahmedabad", "Gandhinagar", "Surat", "Rajkot"])
        
        # Search Queries
        res_d = pd.read_sql("SELECT Name, Contact, BloodGroup, City FROM donors WHERE BloodGroup=? AND City=?", conn, params=(s_bg, s_city))
        res_i = pd.read_sql("SELECT BloodGroup, Quantity, ExpiryDate FROM inventory WHERE BloodGroup=? AND QualityStatus != 'Expired'", conn, params=(s_bg,))
        res_r = pd.read_sql("SELECT Name, BloodGroup, City, RequestDate FROM recipients WHERE BloodGroup=? AND City=?", conn, params=(s_bg, s_city))

        col_left, col_right = st.columns(2)
        with col_left:
            st.write("### 🩸 Available Donors")
            if not res_d.empty: st.table(res_d)
            else: st.info("No individual donors found for this selection.")
            
            st.write("### 📢 Active Blood Requests")
            if not res_r.empty: st.table(res_r)
            else: st.success("No active requests for this blood group in your city.")

        with col_right:
            st.write("### 📦 In-House Stock Status")
            if not res_i.empty: st.table(res_i)
            else: st.warning("Stock currently unavailable for this blood group.")
