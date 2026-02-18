# Simple Banking System (Python + SQLite)

A command-line banking system implemented in Python. The application allows users to create accounts, log in, manage balances, transfer money, and close accounts. All account data is stored locally using SQLite.

## Overview

This project simulates a basic banking system with persistent storage. Each account is identified by a generated card number that follows the Luhn algorithm for validation. The system is menu-driven and operates entirely through a CLI.

## Features

- Create a new bank account
- Automatically generate:
  - 16-digit card number
  - 4-digit PIN
- Validate card numbers with the Luhn algorithm
- Log into an existing account
- Check account balance
- Add income
- Transfer money between accounts
- Close account
- Persist data in a local SQLite database (`card.s3db`)

## Requirements

- Python 3.10+ (recommended)
- No external dependencies (uses Python standard library)

## How to Run

1. Clone the repository:
   - `git clone <your-repository-url>`
   - `cd <your-repository-folder>`

2. Run the program:
   - `python main.py`

## Menus

### Logged Out

1. Create an account  
2. Log into account  
0. Exit  

### Logged In

1. Balance  
2. Add income  
3. Do transfer  
4. Close account  
5. Log out  
0. Exit  

## Card Number Generation

Each card number consists of:
- IIN (Issuer Identification Number): `400000`
- Random 9-digit customer account identifier
- Final check digit computed using the Luhn algorithm

This ensures generated card numbers are structurally valid and can be verified before transfers.

## Database

Database file: `card.s3db`

The application creates the following table if it does not exist:

- Table name: `card`
- Columns:
  - `id` (INTEGER PRIMARY KEY)
  - `number` (TEXT UNIQUE)
  - `pin` (TEXT)
  - `balance` (INTEGER DEFAULT 0)

## Architecture

### State Management

The program uses an enum to track user state:
- `LOGGED_OUT`
- `LOGGED_IN`
- `EXIT`

### Main Classes

Bank
- Creates and resets the database
- Generates card numbers and PINs
- Retrieves accounts from the database
- Updates balances
- Validates transfers (Luhn, existence, self-transfer)
- Deletes accounts

Account
- Stores card number, PIN, and balance
- Persists account records to the database

## Example Workflow

1. Create an account and record the card number + PIN.
2. Log in using the provided credentials.
3. Add income to increase balance.
4. Transfer money to another valid card number.
5. Log out or close the account.

## Development Notes

### Database Reset on Startup

Your current `main()` resets the database every run:

- This is useful for local testing.
- It prevents persistence across runs.

To keep accounts between runs, remove or comment out:

- `current_bank.reset_db()`

## Known Limitations

- PINs are stored in plain text.
- No encryption or hashing is used.
- Transfers are not wrapped in a single database transaction.
- Limited input validation.
- Single-file structure (harder to scale).

## Future Improvements

- Refactor into multiple modules (db layer, services, CLI)
- Store hashed PINs instead of plain text
- Add transaction handling for transfers (atomic updates)
- Add input validation + error handling
- Add unit tests
- Support multiple banks / multiple databases
- Add account types (interest-bearing, checking/savings)

## Suggested Future Structure

- `banking/models.py`
- `banking/services.py`
- `banking/database.py`
- `banking/cli.py`
- `main.py`
