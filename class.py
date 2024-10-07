from pydantic import BaseModel, GetPydanticSchema

# Banking Program

class Bank:
    def __init__(self):
        self.balance_checking = 0
        self.balance_savings = 0

    def show_balance(self):
        while True:
           account = input("1 - Checking | 2 - Savings: ")
           if account == "1":
               return self.balance_checking, "Checking"
           elif account == "2":
               return self.balance_savings, "Savings"
           else:
               print("Incorrect Value, Input '1' for 'Checking' or '2' for 'Savings'.")
               continue


    def deposit(self):
        while True:
            account = input("1 - Checking | 2 - Savings: ")
            if account in ["1", "2"]:
                try:
                    deposit_amount = float(input("Enter Deposit Amount: "))
                    if deposit_amount > 0:
                        if account == "1":
                            self.balance_checking += deposit_amount
                            return self.balance_checking, "Checking", deposit_amount
                        else:
                            self.balance_savings += deposit_amount
                            return self.balance_savings, "Savings", deposit_amount
                    else:
                        print("Invalid Amount, Enter a positive number")
                except Exception as e:
                    print(f"Please enter correct values '1 or '2' for account information")
            else:
                print("Incorrect, please enter '1' for checking or '2' for savings account information.")


    def withdraw(self):
        account = input("1 - Checking | 2 - Savings: ")
        if account in ["1", "2"]:
            withdraw_amt = float(input("Enter Withdraw Amount: "))
            if withdraw_amt > 0:
                if account == 1:
                    if self.balance_checking >= withdraw_amt:
                        self.balance_checking -= withdraw_amt
                        return self.balance_checking, "Checking", withdraw_amt
                    elif self.balance_checking == 0:
                        print("No funds to withdraw\nReturning to Main Menu...")

                    else:
                        print("Insufficient Funds, Try again")


                else:
                    if self.balance_savings >= withdraw_amt:
                        self.balance_savings -= withdraw_amt
                        return self.balance_savings, "Savings", withdraw_amt
                    elif self.balance_savings == 0:
                        print("No funds to withdraw\nReturning to Main Menu...")

                    else:
                        print("Insufficient Funds, Try again")
        else:
            print("Please input '1' or '2' for account selection. ")

    def run(self):
        is_running = True

        while is_running:
            print("\n-Welcome to my Banking Program-")
            print("1: Show Balance \n2: Deposit\n3: Withdraw\n4: Exit\n")

            user_input = input("Select a Option ('1 - 4'): ")

            if user_input == '1':
                result = self.show_balance()
                if result:
                    balance, account_type = result
                    print(f"\nYour {account_type} Balance Is ${balance:.2f}")

            elif user_input == '2':
                result = self.deposit()
                if result:
                    balance, account_type, amount = result
                    print(f"\nYou have deposited ${amount:.2f} into your {account_type} account")

            elif user_input == '3':
                result = self.withdraw()
                if result:
                    balance, account_type, amount = result
                    print(f"\nYou have withdrawn ${amount:.2f} from your {account_type} account")

            elif user_input == '4':
                print("Thank you for using Brian's bank. Goodbye!")
                break
            else:
                print("Invalid option. Please choose a number between 1 and 4.")


if __name__ == "__main__":
     bank = Bank()
     bank.run()
