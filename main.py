import streamlit as st
from saucy import load_lottie_url, background_adjuster
import classes
from database import create_tables

background_adjuster(
    "https://images.pexels.com/photos/164501/pexels-photo-164501.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2")

lottie_url = "https://lottie.host/8b171128-212d-481c-bac1-eabf6d59a748/N4QqT1mr0M.json"
lottie_json = load_lottie_url(lottie_url)


def main():
    global account_type

    conn = classes.create_connection()
    create_tables(conn)

    st.title("Zavala National Bank")

    bank = classes.Bank()

    if st.session_state.current_user is None:
        st.sidebar.title("Login / Register")
        action = st.sidebar.selectbox("Choose an action", ("Login", "Register"))

        if action == "Login":
            username = st.sidebar.text_input("Username")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Login"):
                if bank.login(username, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

        elif action == "Register":
            username = st.sidebar.text_input("Choose a username")
            password = st.sidebar.text_input("Choose a password", type="password")
            email = st.sidebar.text_input("Email")
            phone = st.sidebar.text_input("Phone number")
            if st.sidebar.button("Register"):
                if bank.create_user(username, password, email, phone):
                    st.success("User registered successfully! You can now log in.")
                else:
                    st.error("Registration failed. Please check your information and try again.")

    else:
        st.sidebar.title(f"Welcome, {st.session_state.current_user.username}!")
        if st.sidebar.button("Logout"):
            bank.logout()
            st.rerun()

        operation = st.sidebar.selectbox(
            "Choose an operation",
            ("View Profile", "Show Balance", "Deposit", "Withdraw", "Transfer",
             "Transaction History", "View Beneficiaries", "Manage Beneficiaries", "Update Profile")
        )

        if operation == "View Profile":
            st.subheader("Your Profile")
            profile = bank.get_user_profile()
            st.write(f"Username: {profile['username']}")
            st.write(f"Email: {profile['email'] or 'Not set'}")
            st.write(f"Phone: {profile['phone'] or 'Not set'}")

        elif operation == "View Beneficiaries":
            st.subheader("Your Beneficiaries")
            beneficiaries = bank.get_beneficiaries()
            if beneficiaries:
                for beneficiary in beneficiaries:
                    st.write(f"Name: {beneficiary[2]}")
                    st.write(f"Account Number: {beneficiary[3]}")
                    st.write(f"Bank Name: {beneficiary[4]}")
                    st.write("---")
            else:
                st.write("You haven't added any beneficiaries yet.")

        elif operation == "Show Balance":
            st.subheader("Account Balance")
            account_type = st.selectbox("Choose an account", ("Checking", "Savings"))
            balance = bank.get_balance(account_type)
            st.write(f"Your {account_type} Balance Is ${balance:.2f}")

        elif operation == "Deposit":
            st.subheader("Deposit")
            account_type = st.selectbox("Choose an account", ("Checking", "Savings"))
            amount = st.number_input("Enter Deposit Amount", min_value=0.01, step=0.01)
            if st.button("Deposit"):
                new_balance = bank.deposit(account_type, amount)
                if new_balance is not None:
                    st.success(f"You have deposited ${amount:.2f} into your {account_type} account")
                    st.write(f"New Balance - ${new_balance:.2f}")

        elif operation == "Withdraw":
            st.subheader("Withdraw")
            account_type = st.selectbox("Choose an account", ("Checking", "Savings"))
            amount = st.number_input("Enter Withdraw Amount", min_value=0.01, step=0.01)
            if st.button("Withdraw"):
                new_balance = bank.withdraw(account_type, amount)
                if new_balance is not None:
                    st.success(f"You have withdrawn ${amount:.2f} from your {account_type} account")
                    st.write(f"New Balance - ${new_balance:.2f}")

        elif operation == "Transfer":
            st.subheader("Transfer")
            from_account = st.selectbox("From Account", ("Checking", "Savings"))
            to_account = "Savings" if from_account == "Checking" else "Checking"
            amount = st.number_input("Enter Transfer Amount", min_value=0.01, step=0.01)
            if st.button("Transfer"):
                bank.transfer(from_account, to_account, amount)

        elif operation == "Transaction History":
            st.subheader("Transaction History")
            df = bank.get_transaction_history()
            if not df.empty:
                st.dataframe(df)
            else:
                st.write("No transactions yet.")

        elif operation == "Manage Beneficiaries":
            st.subheader("Manage Beneficiaries")
            beneficiaries = bank.get_beneficiaries()
            if beneficiaries:
                st.write("Your Beneficiaries:")
                for beneficiary in beneficiaries:
                    st.write(f"Name: {beneficiary[1]}, Account: {beneficiary[2]}, Bank: {beneficiary[3]}")
            else:
                st.write("No beneficiaries added yet.")

            st.subheader("Add New Beneficiary")
            name = st.text_input("Beneficiary Name")
            account_number = st.text_input("Account Number")
            bank_name = st.text_input("Bank Name")
            if st.button("Add Beneficiary"):
                bank.add_beneficiary(name, account_number, bank_name)
                st.success("Beneficiary added successfully!")
                st.rerun()

        elif operation == "Update Profile":
            st.subheader("Update Profile")
            email = st.text_input("New Email", value=st.session_state.current_user.email)
            phone = st.text_input("New Phone Number", value=st.session_state.current_user.phone)
            if st.button("Update Profile"):
                if bank.update_profile(email, phone):
                    st.success("Profile updated successfully!")
                else:
                    st.error("Failed to update profile. Please check your information.")

        # Display current balances
        st.sidebar.subheader("Current Balances")
        st.sidebar.write(f"Checking: ${bank.get_balance('Checking'):.2f}")
        st.sidebar.write(f"Savings: ${bank.get_balance('Savings'):.2f}")


if __name__ == "__main__":
    main()