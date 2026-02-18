import os
import sqlite3
from enum import Enum, auto
from random import randrange
from math import ceil

class State(Enum):
    LOGGED_OUT = auto()
    LOGGED_IN = auto()
    EXIT = auto()

class Bank:
    IIN = '400000'

    def __init__(self):
        pass

    @staticmethod
    def create_db():  # implemented as Bank method so future databases can be tied to different banks
        connection = sqlite3.connect('card.s3db')
        curs = connection.cursor()
        curs.execute('CREATE TABLE IF NOT EXISTS card ('
                     'id INTEGER PRIMARY KEY,'
                     'number TEXT UNIQUE,'
                     'pin TEXT,'
                     'balance INTEGER DEFAULT 0'
                     ');')
        connection.commit()
        connection.close()

    @staticmethod
    def reset_db():
        if os.path.exists('card.s3db'):
            os.remove('card.s3db')

    @staticmethod
    def generate_check_digit(first_15_digits) -> str:  # generates check digit using the Luhn algorithm
        first_15_ints = [int(digit) for digit in list(first_15_digits)]  # turn string of digits into list of ints
        multiplied_if_odd_index = [digit * 2 if (n + 1) % 2 else digit  # double digits at odd indices (1-start)
                                   for n, digit in enumerate(first_15_ints)]
        subtracted_if_over_9 = [digit - 9 if digit > 9 else digit for digit in multiplied_if_odd_index]
        rounded_sum_difference = (ceil(sum(subtracted_if_over_9) / 10) * 10
                                  - sum(subtracted_if_over_9))  # subtract rounded sum from next multiple of 10
        check_digit = str(rounded_sum_difference)
        return check_digit

    def create_numbers(self) -> tuple[str, str]:
        customer_account_number = str(randrange(1000000000)).zfill(9)  # random 9 digit string
        first_15_digits = self.IIN + customer_account_number
        check_digit = self.generate_check_digit(first_15_digits)
        credit_card_number: str = (first_15_digits + check_digit)
        pin = str(randrange(10000)).zfill(4)  # random 4 digit string
        return credit_card_number, pin

    def create_account(self) -> 'new account':  # make a new account with this info and add to dict
        credit_card_number,pin = self.create_numbers()
        retrieved_account: 'Account | None' = self.retrieve_account_info(credit_card_number)

        while retrieved_account is not None:  # enter loop and create new number until we have a number not in database
            credit_card_number, pin = self.create_numbers()
            retrieved_account = self.retrieve_account_info(credit_card_number)

        new_account = Account(credit_card_number, pin)  # create new account with new info
        new_account.save_account_to_db()
        return new_account

    @staticmethod
    def retrieve_account_info(credit_card_number: str) -> tuple[str, str, int] | None:  # checks if account exists in card.s3db
        connection = sqlite3.connect('card.s3db')
        curs = connection.cursor()
        curs.execute('SELECT * FROM card where (number = ?);',
                     (credit_card_number,))
        retrieved_account = curs.fetchone()
        connection.close()

        if retrieved_account is not None:
            retrieved_info = retrieved_account[1:]  # ignore database id
            # ccn is 16 digits, pin is 4 digits
            return retrieved_info
        else:
            return None

    @staticmethod
    def check_pin_matches(retrieved_account: "Account", pin_input) -> bool:
        return retrieved_account.pin == pin_input

    def retrieve_account(self, card_number_input, pin_input) -> "Account | None":
        retrieved_info = self.retrieve_account_info(card_number_input)

        if retrieved_info:
            retrieved_credit_card, retrieved_pin, retrieved_balance = retrieved_info
            retrieved_credit_card = str(retrieved_credit_card)
            retrieved_pin = str(retrieved_pin).zfill(4)
            retrieved_account = Account(retrieved_credit_card, retrieved_pin, retrieved_balance)
            pin_matches = self.check_pin_matches(retrieved_account, pin_input)

            if pin_matches:
                return retrieved_account
            else:
                return None
        else:
            return None

    @staticmethod
    def update_balance(account, change):
        account.balance += change

    def add_income(self, account, income_to_add: int) -> str:
        connection = sqlite3.connect('card.s3db')
        curs = connection.cursor()
        curs.execute(
            'UPDATE card SET balance = balance + ? WHERE number = ?',
            (income_to_add, account.credit_card_number)
        )
        connection.commit()
        curs.close()
        self.update_balance(account, income_to_add)
        return 'Income was added!'

    def deduct_balance(self, account, balance_to_deduct: int) -> bool:
        if account.balance >= balance_to_deduct:
            connection = sqlite3.connect('card.s3db')
            curs = connection.cursor()
            curs.execute(
                'UPDATE card SET balance = balance - ? WHERE number = ?',
                (balance_to_deduct, account.credit_card_number)
            )
            connection.commit()
            curs.close()
            self.update_balance(account, -balance_to_deduct)
            return True
        else:
            return False

    def check_transfer_card(self, transfer_card_number, account) -> tuple[bool, str]:
        if self.generate_check_digit(transfer_card_number[:-1]) != transfer_card_number[-1]: # check Luhn algo
            return False, 'Probably you made a mistake in the card number. Please try again!'
        elif transfer_card_number == account.credit_card_number:
            return False, "You can't transfer money to the same account!"
        elif self.retrieve_account_info(transfer_card_number) is None:
            return False, 'Such a card does not exist.'
        else: # executes if card number is valid
            return True, 'Enter how much money you want to transfer:'

    def perform_transfer(self, account, transfer_account, amount_to_transfer) -> str:
        deduct_balance_success = self.deduct_balance(account, amount_to_transfer)
        if deduct_balance_success:
            self.add_income(transfer_account, amount_to_transfer)
            return 'Success!'
        else:
            return 'Not enough money!'

    @staticmethod
    def close_account(account):
        connection = sqlite3.connect('card.s3db')
        curs = connection.cursor()
        curs.execute('DELETE FROM card WHERE number = ?;',(account.credit_card_number,))
        connection.commit()
        connection.close()


class Account:
    def __init__(self, credit_card_number, pin, balance=0):
        self.credit_card_number = credit_card_number
        self.pin = pin
        self.balance = balance

    def save_account_to_db(self) -> None:
        connection = sqlite3.connect('card.s3db')
        curs = connection.cursor()
        curs.execute("INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);",
                     (self.credit_card_number, self.pin, self.balance))
        connection.commit()
        connection.close()


def do_create_account(current_bank):
    new_account = current_bank.create_account()
    return '\n'.join(['Your card has been created',
                     'Your card number:',
                     new_account.credit_card_number,
                     'Your card PIN:',
                     new_account.pin])

def do_add_income(income_to_add, current_bank, current_account):
    add_income_message = current_bank.add_income(current_account, income_to_add)
    return add_income_message

def do_transfer(transfer_card_number, current_bank, current_account):
    valid_card, transfer_card_message = current_bank.check_transfer_card(transfer_card_number, current_account)
    if valid_card:
        transfer_account_pin = current_bank.retrieve_account_info(transfer_card_number)[1]
        transfer_account = current_bank.retrieve_account(transfer_card_number, transfer_account_pin)
        amount_to_transfer = int(input(transfer_card_message + "\n"))
        transfer_status = current_bank.perform_transfer(current_account, transfer_account, amount_to_transfer)
        return transfer_status
    else:
        return transfer_card_message


# user interface and methods
def display_menu(state):
    if state == State.LOGGED_OUT:
        return ('\n'.join(['1. Create an account',
                           '2. Log into account',
                           '0. Exit']))
    if state == State.LOGGED_IN:
        return ('\n'.join(['1. Balance',
                           '2. Add income',
                           '3. Do transfer',
                           '4. Close account',
                           '5. Log out',
                           '0. Exit']))

    return None  # temporary handler that should be replaced with error-catching mechanism

def process_menu_input(menu_selection: str, current_state: State, current_bank: Bank, current_account: Account)\
        -> tuple[State, Account | None]:
    if current_state == State.LOGGED_OUT:
        match menu_selection:
            case "1":  # create account
                create_account_message = do_create_account(current_bank)
                print(create_account_message)

            case "2":  # log in
                card_number_input = input('Enter your card number:\n')
                pin_input = input('Enter your PIN:\n')

                current_account = current_bank.retrieve_account(card_number_input, pin_input)
                if current_account:
                    print('You have successfully logged in!')
                    current_state = State.LOGGED_IN
                else:
                    print('Wrong card number or PIN!')
                    current_state = State.LOGGED_OUT

            case "0":  # exit
                print("Bye!")
                current_state = State.EXIT

    elif current_state == State.LOGGED_IN:
        match menu_selection:
            case "1":  # retrieve balance
                print("Balance:", current_account.balance)

            case "2":  # add income
                income_to_add = int(input("Enter income:\n"))
                add_income_message = do_add_income(income_to_add, current_bank, current_account)
                print(add_income_message)

            case "3":  # perform transfer
                transfer_card_number = input("Enter card number:\n")
                transfer_message = do_transfer(transfer_card_number, current_bank, current_account)
                print(transfer_message)

            case "4":  # close account
                current_bank.close_account(current_account)
                print('The account has been closed')
                current_state = State.LOGGED_OUT

            case "5":  # log out
                current_account = None
                print('You have successfully logged out!')
                current_state = State.LOGGED_OUT

            case "0":  # exit
                print("Bye!")
                current_state = State.EXIT

    return current_state, current_account  # currently remains in current state if no valid options provided


def main():
    current_bank: Bank = Bank()

    current_bank.reset_db()  # implemented for local testing
    current_bank.create_db()

    current_account: Account | None = None
    state = State.LOGGED_OUT

    while state != State.EXIT:
        print(display_menu(state))
        menu_selection = input()
        state, current_account = process_menu_input(menu_selection, state, current_bank, current_account)

if __name__ == "__main__":
    main()

# next steps:
# improve code quality,
# add new features,
# add multiple banks with unique databases,
# introduce cryptographic protocols,
# introduce various account types with interest
