import streamlit as st
import pandas as pd
import hashlib
import uuid
import re
from datetime import datetime
from database import (create_connection, get_beneficiaries, update_user_profile,
                      add_user, add_beneficiary,
                      add_transaction, get_user, update_balance, get_transactions)



class User:
    def __init__(self, username, password_hash, user_id=None, checking_balance=0, savings_balance=0, email=None, phone=None):
        self.username = username
        self.password_hash = password_hash
        self.user_id = user_id or str(uuid.uuid4())
        self.checking_balance = checking_balance
        self.savings_balance = savings_balance
        self.email = email
        self.phone = phone

class Bank:
    def __init__(self):
        self.conn = create_connection()
        if 'current_user' not in st.session_state:
            st.session_state.current_user = None
        self.transaction_limit = 1000  # Daily transaction limit

    def create_user(self, username, password, email, phone):
        if get_user(self.conn, username):
            return False
        if not self.validate_email(email) or not self.validate_phone(phone):
            return False
        password_hash = self.hash_password(password)
        new_user = User(username, password_hash, email=email, phone=phone)
        add_user(self.conn, new_user)
        return True

    def login(self, username, password):
        user_data = get_user(self.conn, username)
        if user_data:
            stored_password_hash = user_data[2]
            if self.verify_password(password, stored_password_hash):
                # Create User object with available data, using default values if not present
                st.session_state.current_user = User(
                    username=username,
                    password_hash=stored_password_hash,
                    user_id=user_data[0] if len(user_data) > 0 else None,
                    checking_balance=user_data[3] if len(user_data) > 3 else 0,
                    savings_balance=user_data[4] if len(user_data) > 4 else 0,
                    email=user_data[5] if len(user_data) > 5 else None,
                    phone=user_data[6] if len(user_data) > 6 else None
                )
                return True
        return False

    def logout(self):
        st.session_state.current_user = None

    def get_balance(self, account_type):
        if account_type == "Checking":
            return st.session_state.current_user.checking_balance
        elif account_type == "Savings":
            return st.session_state.current_user.savings_balance

    def deposit(self, account_type, amount):
        global new_balance
        if amount > 0:
            if account_type == "Checking":
                new_balance = st.session_state.current_user.checking_balance + amount
                update_balance(self.conn, st.session_state.current_user.user_id, account_type, new_balance)
                st.session_state.current_user.checking_balance = new_balance
                self.add_transaction("Deposit", account_type, amount)
            elif account_type == "Savings":
                new_balance = st.session_state.current_user.savings_balance + amount
                update_balance(self.conn, st.session_state.current_user.user_id, account_type, new_balance)
                st.session_state.current_user.savings_balance = new_balance
                self.add_transaction("Deposit", account_type, amount)
            return new_balance
        else:
            st.error("Invalid Amount. Please enter a positive number.")

    def withdraw(self, account_type, amount):
        if amount > 0:
            if self.check_transaction_limit(amount):
                if account_type == "Checking":
                    if st.session_state.current_user.checking_balance >= amount:
                        new_balance = st.session_state.current_user.checking_balance - amount
                        st.session_state.current_user.checking_balance = new_balance
                        update_balance(self.conn, st.session_state.current_user.user_id, account_type, new_balance)
                        self.add_transaction("Withdrawal", account_type, -amount)
                        return new_balance
                    else:
                        st.error("Insufficient funds in Checking account.")
                elif account_type == "Savings":
                    if st.session_state.current_user.savings_balance >= amount:
                        new_balance = st.session_state.current_user.savings_balance - amount
                        update_balance(self.conn, st.session_state.current_user.user_id, account_type, new_balance)
                        st.session_state.current_user.savings_balance = new_balance
                        self.add_transaction("Withdrawal", account_type, -amount)
                        return new_balance
                    else:
                        st.error("Insufficient funds in Savings account.")
            else:
                st.error(f"Transaction exceeds daily limit of ${self.transaction_limit}.")
        else:
            st.error("Invalid Amount. Please enter a positive number.")

    def add_transaction(self, transaction_type, account_type, amount):
        transaction = {
            "user_id": st.session_state.current_user.user_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": transaction_type,
            "account": account_type,
            "amount": amount
        }
        add_transaction(self.conn, transaction)

    def get_transaction_history(self):
        transactions = get_transactions(self.conn, st.session_state.current_user.user_id)
        return pd.DataFrame(transactions, columns=["Date", "Type", "Account", "Amount"])

    def transfer(self, from_account, to_account, amount):
        if amount > 0:
            if self.check_transaction_limit(amount):
                if from_account == "Checking" and st.session_state.current_user.checking_balance >= amount:
                    self.withdraw("Checking", amount)
                    self.deposit("Savings", amount)
                    st.success(f"Successfully transferred ${amount:.2f} from Checking to Savings.")
                elif from_account == "Savings" and st.session_state.current_user.savings_balance >= amount:
                    self.withdraw("Savings", amount)
                    self.deposit("Checking", amount)
                    st.success(f"Successfully transferred ${amount:.2f} from Savings to Checking.")
                else:
                    st.error("Insufficient funds for transfer.")
            else:
                st.error(f"Transfer exceeds daily limit of ${self.transaction_limit}.")
        else:
            st.error("Invalid Amount. Please enter a positive number.")

    def add_beneficiary(self, name, account_number, bank_name):
        beneficiary = {
            "user_id": st.session_state.current_user.user_id,
            "name": name,
            "account_number": account_number,
            "bank_name": bank_name
        }
        add_beneficiary(self.conn, beneficiary)


    def get_user_profile(self):
        if st.session_state.current_user:
            return {
                "username": st.session_state.current_user.username,
                "email": st.session_state.current_user.email,
                "phone": st.session_state.current_user.phone
            }
        return None

    def get_beneficiaries(self):
        if st.session_state.current_user:
            return get_beneficiaries(self.conn, st.session_state.current_user.user_id)
        return []

    def update_profile(self, email, phone):
        if self.validate_email(email) and self.validate_phone(phone):
            update_user_profile(self.conn, st.session_state.current_user.user_id, email, phone)
            st.session_state.current_user.email = email
            st.session_state.current_user.phone = phone
            return True
        return False


    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password, hashed_password):
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password

    @staticmethod
    def validate_email(email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone):
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None

    def check_transaction_limit(self, amount):
        today = datetime.now().date()
        daily_transactions = [t for t in get_transactions(self.conn, st.session_state.current_user.user_id)
                              if datetime.strptime(t[0], "%Y-%m-%d %H:%M:%S").date() == today]
        daily_total = sum(abs(t[3]) for t in daily_transactions)
        return (daily_total + amount) <= self.transaction_limit