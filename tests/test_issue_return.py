#!/usr/bin/env python3
# tests/test_issue_return.py
"""
Tests for the Library Management System.
Tests for issuing and returning books.
"""

import os
import shutil
import unittest
from datetime import datetime, timedelta
from models import Book, Member, Loan
from storage import BookStorage, MemberStorage, LoanStorage
from library import Library


class TestIssueReturn(unittest.TestCase):
    """Test case for issuing and returning books."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary test directory
        self.test_dir = "./test_data"
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.makedirs(self.test_dir)
        
        # Create test data
        self.library = Library(self.test_dir)
        self.book_storage = BookStorage(self.test_dir)
        self.member_storage = MemberStorage(self.test_dir)
        self.loan_storage = LoanStorage(self.test_dir)
        
        # Add a test book
        self.test_book = Book(
            isbn="9780132350884",
            title="Clean Code",
            author="Robert C. Martin",
            copies_total=5,
            copies_available=5
        )
        self.book_storage.add_item(self.test_book)
        
        # Add a test member
        self.test_member = Member(
            member_id="1001",
            name="Test User",
            password_hash="$2b$12$test_hash",
            email="test@example.com",
            join_date=datetime.now()
        )
        self.member_storage.add_item(self.test_member)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the test directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_issue_book(self):
        """Test issuing a book."""
        # Issue the book
        success, _ = self.library.issue_book(self.test_book.isbn, self.test_member.member_id)
        self.assertTrue(success)
        
        # Check that the available copies decreased
        book = self.book_storage.get_item_by_id(self.test_book.isbn)
        self.assertEqual(book.copies_available, 4)
        
        # Check that a loan was created
        loans = self.loan_storage.get_loans_for_book(self.test_book.isbn)
        self.assertEqual(len(loans), 1)
        self.assertEqual(loans[0].member_id, self.test_member.member_id)
        self.assertEqual(loans[0].isbn, self.test_book.isbn)
        self.assertIsNone(loans[0].return_date)
    
    def test_issue_unavailable_book(self):
        """Test issuing a book with no available copies."""
        # Set available copies to 0
        self.test_book.copies_available = 0
        self.book_storage.update_item(self.test_book)
        
        # Try to issue the book
        success, _ = self.library.issue_book(self.test_book.isbn, self.test_member.member_id)
        self.assertFalse(success)
        
        # Check that no loan was created
        loans = self.loan_storage.get_loans_for_book(self.test_book.isbn)
        self.assertEqual(len(loans), 0)
    
    def test_return_book(self):
        """Test returning a book."""
        # Issue the book first
        success, _ = self.library.issue_book(self.test_book.isbn, self.test_member.member_id)
        self.assertTrue(success)
        
        # Get the loan ID
        loans = self.loan_storage.get_loans_for_book(self.test_book.isbn)
        loan_id = loans[0].loan_id
        
        # Return the book
        success, _ = self.library.return_book(loan_id)
        self.assertTrue(success)
        
        # Check that the available copies increased
        book = self.book_storage.get_item_by_id(self.test_book.isbn)
        self.assertEqual(book.copies_available, 5)
        
        # Check that the loan was updated
        loan = self.loan_storage.get_item_by_id(loan_id)
        self.assertIsNotNone(loan.return_date)
    
    def test_issue_return_multiple(self):
        """Test issuing and returning multiple copies of the same book."""
        # Issue two copies
        success1, _ = self.library.issue_book(self.test_book.isbn, self.test_member.member_id)
        self.assertTrue(success1)
        
        success2, _ = self.library.issue_book(self.test_book.isbn, self.test_member.member_id)
        self.assertTrue(success2)
        
        # Check that the available copies decreased correctly
        book = self.book_storage.get_item_by_id(self.test_book.isbn)
        self.assertEqual(book.copies_available, 3)
        
        # Get the loan IDs
        loans = self.loan_storage.get_loans_for_book(self.test_book.isbn)
        self.assertEqual(len(loans), 2)
        
        # Return the first book
        success, _ = self.library.return_book(loans[0].loan_id)
        self.assertTrue(success)
        
        # Check that the available copies increased
        book = self.book_storage.get_item_by_id(self.test_book.isbn)
        self.assertEqual(book.copies_available, 4)
        
        # Return the second book
        success, _ = self.library.return_book(loans[1].loan_id)
        self.assertTrue(success)
        
        # Check that the available copies are back to the original value
        book = self.book_storage.get_item_by_id(self.test_book.isbn)
        self.assertEqual(book.copies_available, 5)
    
    def test_overdue_detection(self):
        """Test detection of overdue books."""
        # Issue the book
        success, _ = self.library.issue_book(self.test_book.isbn, self.test_member.member_id)
        self.assertTrue(success)
        
        # Get the loan and modify the due date to make it overdue
        loans = self.loan_storage.get_loans_for_book(self.test_book.isbn)
        loan = loans[0]
        loan.due_date = datetime.now() - timedelta(days=1)
        self.loan_storage.update_item(loan)
        
        # Check if the loan is detected as overdue
        overdue_loans = self.library.get_overdue_loans()
        self.assertEqual(len(overdue_loans), 1)
        self.assertEqual(overdue_loans[0][0].loan_id, loan.loan_id)


if __name__ == '__main__':
    unittest.main()
