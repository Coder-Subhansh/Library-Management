#!/usr/bin/env python3
# main.py
"""
Main entry point for the Library Management System.
Handles the CLI interface and integrates all modules.
"""

import os
import sys
import argparse
from datetime import datetime
from tabulate import tabulate
from models import Book, Member, Loan
from storage import BookStorage, MemberStorage, LoanStorage
from library import Library
from auth import (
    register_member, login, logout, is_logged_in,
    get_current_user_id, get_current_user_role, require_login
)


class LibraryManagementSystem:
    """Main class for the Library Management System CLI."""
    
    def __init__(self, data_dir: str):
        """
        Initialize the Library Management System.
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = data_dir
        self.library = Library(data_dir)
    
    def start(self):
        """Start the Library Management System."""
        print("\n" + "=" * 50)
        print("📚 Welcome to the Library Management System 📚")
        print("=" * 50)
        
        while True:
            if not is_logged_in():
                self.show_login_menu()
            else:
                role = get_current_user_role()
                if role == 'librarian':
                    self.show_librarian_menu()
                elif role == 'member':
                    self.show_member_menu()
                else:
                    print("Error: Unknown role")
                    logout()
    
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def show_login_menu(self):
        """Show the login menu."""
        print("\n=== Login Menu ===")
        print("1. Login as Librarian")
        print("2. Login as Member")
        print("3. Register as Member")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '1':
            self.librarian_login()
        elif choice == '2':
            self.member_login()
        elif choice == '3':
            self.register_member()
        elif choice == '4':
            print("\nThank you for using the Library Management System. Goodbye!")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
    
    def librarian_login(self):
        """Handle librarian login."""
        print("\n=== Librarian Login ===")
        username = input("Username: ")
        password = input("Password: ")
        
        success, message = login(self.data_dir, username, password, 'librarian')
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def member_login(self):
        """Handle member login."""
        print("\n=== Member Login ===")
        id_or_email = input("Member ID or Email: ")
        password = input("Password: ")
        
        success, message = login(self.data_dir, id_or_email, password, 'member')
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def register_member(self):
        """Handle member registration."""
        print("\n=== Member Registration ===")
        name = input("Name: ")
        email = input("Email: ")
        password = input("Password: ")
        confirm_password = input("Confirm Password: ")
        
        success, message = register_member(self.data_dir, name, email, password, confirm_password)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def show_librarian_menu(self):
        """Show the librarian menu."""
        print("\n=== Librarian Dashboard ===")
        print("1. Add Book")
        print("2. Remove Book")
        print("3. Issue Book")
        print("4. Return Book")
        print("5. View Overdue List")
        print("6. Register Member")
        print("7. Search Books")
        print("8. View All Books")
        print("9. View All Members")
        print("10. Logout")
        
        choice = input("\nEnter your choice (1-10): ")
        
        if choice == '1':
            self.add_book()
        elif choice == '2':
            self.remove_book()
        elif choice == '3':
            self.issue_book()
        elif choice == '4':
            self.return_book()
        elif choice == '5':
            self.view_overdue_list()
        elif choice == '6':
            self.register_member()
        elif choice == '7':
            self.search_books()
        elif choice == '8':
            self.view_all_books()
        elif choice == '9':
            self.view_all_members()
        elif choice == '10':
            logout()
            print("\n✅ Logged out successfully.")
        else:
            print("\nInvalid choice. Please try again.")
    
    def show_member_menu(self):
        """Show the member menu."""
        print(f"\n=== Member Dashboard ===")
        print("1. Search Books")
        print("2. Borrow Book")
        print("3. My Loans")
        print("4. My Loan History")
        print("5. Logout")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            self.search_books()
        elif choice == '2':
            self.borrow_book()
        elif choice == '3':
            self.view_my_loans()
        elif choice == '4':
            self.view_loan_history()
        elif choice == '5':
            logout()
            print("\n✅ Logged out successfully.")
        else:
            print("\nInvalid choice. Please try again.")
    
    # Librarian functions
    
    def add_book(self):
        """Add a new book."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== Add Book ===")
        isbn = input("ISBN: ")
        title = input("Title: ")
        author = input("Author: ")
        
        try:
            copies = int(input("Number of Copies: "))
        except ValueError:
            print("\n❌ Number of copies must be a positive integer.")
            return
        
        success, message = self.library.add_book(isbn, title, author, copies)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def remove_book(self):
        """Remove a book."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== Remove Book ===")
        isbn = input("ISBN: ")
        
        success, message = self.library.delete_book(isbn)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def issue_book(self):
        """Issue a book to a member."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== Issue Book ===")
        isbn = input("ISBN to issue: ")
        member_id = input("Member ID: ")
        
        success, message = self.library.issue_book(isbn, member_id)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def return_book(self):
        """Return a book."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== Return Book ===")
        loan_id = input("Loan ID: ")
        
        success, message = self.library.return_book(loan_id)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def view_overdue_list(self):
        """View the list of overdue loans."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== Overdue Books ===")
        overdue_loans = self.library.get_overdue_loans()
        
        if not overdue_loans:
            print("\nNo overdue books.")
            return
        
        # Prepare table data
        table_data = []
        for loan, book, member in overdue_loans:
            days_overdue = (datetime.now() - loan.due_date).days
            table_data.append([
                loan.loan_id,
                book.isbn,
                book.title,
                member.member_id,
                member.name,
                loan.due_date.strftime('%Y-%m-%d'),
                f"{days_overdue} days"
            ])
        
        # Print the table
        print(tabulate(
            table_data,
            headers=["Loan ID", "ISBN", "Title", "Member ID", "Member Name", "Due Date", "Overdue"],
            tablefmt="grid"
        ))
    
    def view_all_books(self):
        """View all books."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== All Books ===")
        books = self.library.get_all_books()
        
        if not books:
            print("\nNo books in the library.")
            return
        
        # Prepare table data
        table_data = []
        for book in books:
            table_data.append([
                book.isbn,
                book.title,
                book.author,
                book.copies_total,
                book.copies_available
            ])
        
        # Print the table
        print(tabulate(
            table_data,
            headers=["ISBN", "Title", "Author", "Total Copies", "Available Copies"],
            tablefmt="grid"
        ))
    
    def view_all_members(self):
        """View all members."""
        success, message = require_login('librarian')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== All Members ===")
        members = self.library.get_all_members()
        
        if not members:
            print("\nNo members registered.")
            return
        
        # Prepare table data
        table_data = []
        for member in members:
            table_data.append([
                member.member_id,
                member.name,
                member.email,
                member.join_date.strftime('%Y-%m-%d')
            ])
        
        # Print the table
        print(tabulate(
            table_data,
            headers=["Member ID", "Name", "Email", "Join Date"],
            tablefmt="grid"
        ))
    
    # Member functions
    
    def search_books(self):
        """Search for books."""
        print("\n=== Search Books ===")
        keyword = input("Enter search term (title or author): ")
        
        books = self.library.search_books(keyword)
        
        if not books:
            print(f"\nNo books found matching '{keyword}'")
            return
        
        # Prepare table data
        table_data = []
        for book in books:
            table_data.append([
                book.isbn,
                book.title,
                book.author,
                book.copies_available,
                "Available" if book.copies_available > 0 else "Not Available"
            ])
        
        # Print the table
        print(tabulate(
            table_data,
            headers=["ISBN", "Title", "Author", "Available Copies", "Status"],
            tablefmt="grid"
        ))
    
    def borrow_book(self):
        """Borrow a book (for members)."""
        success, message = require_login('member')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== Borrow Book ===")
        isbn = input("Enter ISBN of book to borrow: ")
        
        # Get current member ID
        member_id = get_current_user_id()
        
        success, message = self.library.issue_book(isbn, member_id)
        
        if success:
            print(f"\n✅ {message}")
        else:
            print(f"\n❌ {message}")
    
    def view_my_loans(self):
        """View current loans for the logged-in member."""
        success, message = require_login('member')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== My Current Loans ===")
        member_id = get_current_user_id()
        loans = self.library.get_member_loans(member_id)
        
        if not loans:
            print("\nYou have no active loans.")
            return
        
        # Prepare table data
        table_data = []
        for loan, book in loans:
            table_data.append([
                loan.loan_id,
                book.isbn,
                book.title,
                book.author,
                loan.issue_date.strftime('%Y-%m-%d'),
                loan.due_date.strftime('%Y-%m-%d'),
                "Yes" if loan.is_overdue() else "No"
            ])
        
        # Print the table
        print(tabulate(
            table_data,
            headers=["Loan ID", "ISBN", "Title", "Author", "Issue Date", "Due Date", "Overdue"],
            tablefmt="grid"
        ))
    
    def view_loan_history(self):
        """View loan history for the logged-in member."""
        success, message = require_login('member')
        if not success:
            print(f"\n❌ {message}")
            return
        
        print("\n=== My Loan History ===")
        member_id = get_current_user_id()
        loans = self.library.get_loan_history(member_id)
        
        if not loans:
            print("\nYou have no loan history.")
            return
        
        # Prepare table data
        table_data = []
        for loan, book in loans:
            table_data.append([
                loan.loan_id,
                book.isbn,
                book.title,
                loan.issue_date.strftime('%Y-%m-%d'),
                loan.due_date.strftime('%Y-%m-%d'),
                loan.return_date.strftime('%Y-%m-%d') if loan.return_date else "Not Returned"
            ])
        
        # Print the table
        print(tabulate(
            table_data,
            headers=["Loan ID", "ISBN", "Title", "Issue Date", "Due Date", "Return Date"],
            tablefmt="grid"
        ))


def main():
    """Main entry point."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Library Management System')
    parser.add_argument('--data-dir', dest='data_dir', default='./data',
                      help='Directory containing CSV files (default: ./data)')
    
    args = parser.parse_args()
    
    # Create and start the Library Management System
    lms = LibraryManagementSystem(args.data_dir)
    
    try:
        lms.start()
    except KeyboardInterrupt:
        print("\nExiting Library Management System. Goodbye!")
        sys.exit(0)


if __name__ == '__main__':
    main()
