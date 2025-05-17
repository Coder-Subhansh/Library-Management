README.md: Library Management System
Project Overview
This Library Management System is a Python-based console application that allows libraries to manage their collection of books, members, and loans. The system supports two roles (librarian and member) with appropriate permissions, and implements all required business logic for book lending and returns.

Features
Librarian Features
Add new books to the system
Remove books from the system
Register new library members
Issue books to members
Process book returns
View list of overdue books
View all books in the library
View all registered members
Member Features
Search the book catalogue by title or author
Borrow available books
View personal active loans
View personal loan history
Technical Implementation
Data Storage
The system uses CSV files as a mini-database:

books.csv: Stores book information (ISBN, title, author, total and available copies)
members.csv: Stores member details (ID, name, hashed password, email, join date)
loans.csv: Stores loan records (loan ID, member ID, ISBN, issue date, due date, return date)
Security
Passwords are securely hashed using bcrypt
Role-based access control for different user types
Session management for user authentication
Key Algorithms and Data Structures
Implementation of search algorithms for books and members
Date calculations for loan periods and overdue detection
Data validation for input fields
CRUD operations for all entities
Project Structure
The project follows a modular design:

models.py: Contains data models (Book, Member, Loan classes)
storage.py: Handles CSV file I/O operations
auth.py: Manages authentication and user sessions
library.py: Implements the core library functionality
main.py: Provides the command-line interface
tests/: Contains unit tests for system validation
Running the Application
bash
# Install required packages
pip install tabulate bcrypt

# Run the application
python main.py

# Run with custom data directory
python main.py --data-dir ./my_data

# Run tests
python -m tests.test_issue_return
Business Rules
Books have an ISBN, title, author, and number of copies
Each book can have multiple copies available for lending
Members need to register with name, email, and password
Loans have a 14-day period by default
Overdue books are flagged for follow-up
When a book is issued, available copies are decremented
When a book is returned, available copies are incremented
Future Enhancements
Email notification system for overdue books
Fine calculation for late returns
Book reservations and waitlists
Advanced search capabilities
Web interface for easier access
Database integration for better scalability
Author
This Library Management System was created as a semester project using Python, applying data structures and algorithms learned in class.

