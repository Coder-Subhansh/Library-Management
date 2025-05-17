#!/usr/bin/env python3
# library.py
"""
Core library functionality for the Library Management System.
Contains functions for managing books, members, and loans.
"""

from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from models import Book, Member, Loan
from storage import BookStorage, MemberStorage, LoanStorage


class Library:
    """Library class that encapsulates all library functionality."""
    
    def __init__(self, data_dir: str):
        """
        Initialize the library.
        
        Args:
            data_dir: Directory containing CSV files
        """
        self.data_dir = data_dir
        self.book_storage = BookStorage(data_dir)
        self.member_storage = MemberStorage(data_dir)
        self.loan_storage = LoanStorage(data_dir)
    
    # Book management
    
    def add_book(self, isbn: str, title: str, author: str, copies: int) -> Tuple[bool, str]:
        """
        Add a new book to the library.
        
        Args:
            isbn: ISBN of the book
            title: Title of the book
            author: Author of the book
            copies: Number of copies
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Validate input
            if not isbn or not title or not author or copies <= 0:
                return False, "All fields are required and copies must be positive"
            
            # Create a new Book instance
            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                copies_total=copies,
                copies_available=copies
            )
            
            # Add the book to storage
            self.book_storage.add_item(book)
            
            return True, f"Book '{title}' added successfully"
        except ValueError as e:
            return False, f"Failed to add book: {str(e)}"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"
    
    def delete_book(self, isbn: str) -> Tuple[bool, str]:
        """
        Delete a book from the library.
        
        Args:
            isbn: ISBN of the book
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Check if the book exists
            book = self.book_storage.get_item_by_id(isbn)
            if not book:
                return False, f"Book with ISBN {isbn} not found"
            
            # Check if the book can be deleted (no active loans)
            loans = self.loan_storage.get_loans_for_book(isbn)
            active_loans = [loan for loan in loans if not loan.return_date]
            if active_loans:
                return False, f"Cannot delete book: {len(active_loans)} copies currently on loan"
            
            # Delete the book
            self.book_storage.delete_item(isbn)
            
            return True, f"Book '{book.title}' deleted successfully"
        except Exception as e:
            return False, f"An error occurred: {str(e)}"
    
    def search_books(self, keyword: str) -> List[Book]:
        """
        Search for books by title or author.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching books
        """
        return self.book_storage.search_by_title_or_author(keyword)
    
    def get_all_books(self) -> List[Book]:
        """
        Get all books in the library.
        
        Returns:
            List of all books
        """
        return self.book_storage.load_all()
    
    def get_book(self, isbn: str) -> Optional[Book]:
        """
        Get a book by ISBN.
        
        Args:
            isbn: ISBN of the book
            
        Returns:
            Book if found, None otherwise
        """
        return self.book_storage.get_item_by_id(isbn)
    
    # Member management
    
    def get_all_members(self) -> List[Member]:
        """
        Get all members.
        
        Returns:
            List of all members
        """
        return self.member_storage.load_all()
    
    def get_member(self, member_id: str) -> Optional[Member]:
        """
        Get a member by ID.
        
        Args:
            member_id: ID of the member
            
        Returns:
            Member if found, None otherwise
        """
        return self.member_storage.get_item_by_id(member_id)
    
    # Loan management
    
    def issue_book(self, isbn: str, member_id: str) -> Tuple[bool, str]:
        """
        Issue a book to a member.
        
        Args:
            isbn: ISBN of the book
            member_id: ID of the member
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Check if the book exists
            book = self.book_storage.get_item_by_id(isbn)
            if not book:
                return False, f"Book with ISBN {isbn} not found"
            
            # Check if the member exists
            member = self.member_storage.get_item_by_id(member_id)
            if not member:
                return False, f"Member with ID {member_id} not found"
            
            # Check if the book is available
            if book.copies_available <= 0:
                return False, f"Book '{book.title}' is not available"
            
            # Create a new loan
            loan_id = self.loan_storage.generate_loan_id()
            issue_date = datetime.now()
            due_date = issue_date + timedelta(days=14)
            
            loan = Loan(
                loan_id=loan_id,
                member_id=member_id,
                isbn=isbn,
                issue_date=issue_date,
                due_date=due_date,
                return_date=None
            )
            
            # Update book availability
            book.copies_available -= 1
            self.book_storage.update_item(book)
            
            # Add the loan
            self.loan_storage.add_item(loan)
            
            return True, f"Book '{book.title}' issued to {member.name} successfully. Due on {due_date.strftime('%d-%b-%Y')}."
        except Exception as e:
            return False, f"An error occurred: {str(e)}"
    
    def return_book(self, loan_id: str) -> Tuple[bool, str]:
        """
        Return a book.
        
        Args:
            loan_id: ID of the loan
            
        Returns:
            Tuple (success, message)
        """
        try:
            # Check if the loan exists
            loan = self.loan_storage.get_item_by_id(loan_id)
            if not loan:
                return False, f"Loan with ID {loan_id} not found"
            
            # Check if the loan is already returned
            if loan.return_date:
                return False, f"Book already returned on {loan.return_date.strftime('%d-%b-%Y')}"
            
            # Get the book
            book = self.book_storage.get_item_by_id(loan.isbn)
            if not book:
                return False, f"Book with ISBN {loan.isbn} not found"
            
            # Get the member
            member = self.member_storage.get_item_by_id(loan.member_id)
            if not member:
                return False, f"Member with ID {loan.member_id} not found"
            
            # Update the loan
            loan.return_date = datetime.now()
            self.loan_storage.update_item(loan)
            
            # Update book availability
            book.copies_available += 1
            self.book_storage.update_item(book)
            
            # Check if the book is overdue
            if loan.is_overdue():
                days_overdue = (datetime.now() - loan.due_date).days
                return True, f"Book '{book.title}' returned by {member.name}. The book was {days_overdue} days overdue."
            else:
                return True, f"Book '{book.title}' returned by {member.name} successfully."
        except Exception as e:
            return False, f"An error occurred: {str(e)}"
    
    def get_overdue_loans(self) -> List[Tuple[Loan, Book, Member]]:
        """
        Get all overdue loans with book and member details.
        
        Returns:
            List of tuples (loan, book, member)
        """
        overdue_loans = self.loan_storage.get_overdue_loans()
        result = []
        
        for loan in overdue_loans:
            book = self.book_storage.get_item_by_id(loan.isbn)
            member = self.member_storage.get_item_by_id(loan.member_id)
            if book and member:
                result.append((loan, book, member))
        
        return result
    
    def get_member_loans(self, member_id: str) -> List[Tuple[Loan, Book]]:
        """
        Get all loans for a member with book details.
        
        Args:
            member_id: ID of the member
            
        Returns:
            List of tuples (loan, book)
        """
        loans = self.loan_storage.get_active_loans_for_member(member_id)
        result = []
        
        for loan in loans:
            book = self.book_storage.get_item_by_id(loan.isbn)
            if book:
                result.append((loan, book))
        
        return result
    
    def get_loan_history(self, member_id: str) -> List[Tuple[Loan, Book]]:
        """
        Get loan history for a member.
        
        Args:
            member_id: ID of the member
            
        Returns:
            List of tuples (loan, book)
        """
        all_loans = self.loan_storage.load_all()
        member_loans = [loan for loan in all_loans if loan.member_id == member_id]
        result = []
        
        for loan in member_loans:
            book = self.book_storage.get_item_by_id(loan.isbn)
            if book:
                result.append((loan, book))
        
        return result
