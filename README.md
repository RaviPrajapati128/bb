# 🏥 VitalFlow: Smart Blood Bank Management System

VitalFlow is a **Streamlit-based web application** designed to manage blood donors, recipients, hospitals, inventory, and transactions in a secure and user-friendly way. It provides both **admin dashboards** for managing records and a **public search view** for users to check availability of donors, requests, and stock.

---

## 🚀 Features

### 🔐 Authentication
- Secure **login/signup system** with SHA256 password hashing.
- Role-based access: **Admin Dashboard** vs **Public Search View**.

### 📊 Admin Dashboard
- **Home Tab**: Quick statistics on donors, requests, and inventory.
- **Donors Tab**: Register new donors, view donor database, and remove records.
- **Requests Tab**: Manage patient blood requests.
- **Hospitals Tab**: Register partnered hospitals and manage hospital records.
- **Inventory Tab**: Track blood stock, add new units, and manage expiry dates.
- **Transactions Tab**: Record dispatches and track blood transactions.

### 🌍 Public Dashboard
- Search donors, requests, and inventory by **blood group** and **city**.
- Displays available donors, active requests, and in-house stock status.

---

## 🛠️ Tech Stack

- **Frontend/UI**: [Streamlit](https://streamlit.io/)  
- **Database**: SQLite  
- **Libraries**:  
  - `pandas` for data handling  
  - `datetime` for date operations  
  - `hashlib` for password hashing  
  - `random` for utility functions  

---

## 📂 Database Schema

- **users**: Stores usernames and hashed passwords.  
- **donors**: Donor details (Name, Age, Gender, Blood Group, Contact, City, DonatedDate).  
- **recipients**: Patient requests (Name, Age, Gender, Blood Group, Contact, City, RequestDate).  
- **hospitals**: Partnered hospitals (Name, Location, Contact).  
- **inventory**: Blood stock (Blood Group, Quantity, CollectionDate, ExpiryDate, QualityStatus).  
- **transactions**: Dispatch records (RecipientID, DonorID, BloodGroup, Quantity, Date).  
