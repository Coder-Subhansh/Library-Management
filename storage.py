#!/usr/bin/env python3
# storage.py
"""
Storage module for the Library Management System.
Handles reading from and writing to CSV files.
"""

import csv
import os
from typing import List, Dict, Optional, Type, TypeVar, Generic
from models import Book, Member, Loan
from datetime import datetime

# Type variable for generic functions
T = TypeVar('T', Book, Member, Loan)


class Storage(Generic[T]):
    """Generic storage class for reading/writing data models to CSV files."""
    
    def __init__(self, data_dir: str, filename: str, model_class: Type[T]):
        """
        Initialize storage for a specific model type.
        
        Args:
            data_dir: Directory containing CSV files
            filename: Name of the CSV file
            model_class: Class of the model (Book, Member, or Loan)
        """
        self.data_dir = data_dir
        self.filepath = os.path.join(data_dir, filename)
        self.model_class = model_class
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """Create the data directory if it doesn't exist."""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create an empty file if it doesn't exist
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='') as file:
                if self.model_class == Book:
                    writer = csv.writer(file)
                    writer.writerow(['ISBN', 'Title', 'Author', 'CopiesTotal', 'CopiesAvailable'])
                elif self.model_class == Member:
                    writer = csv.writer(file)
                    writer.writerow(['MemberID', 'Name', 'PasswordHash', 'Email', 'JoinDate'])
                elif self.model_class == Loan:
                    writer = csv.writer(file)
                    writer.writerow(['LoanID', 'MemberID', 'ISBN', 'IssueDate', 'DueDate', 'ReturnDate'])
    
    def load_all(self) -> List[T]:
        """
        Load all items from the CSV file.
        
        Returns:
            List of model instances (Book, Member, or Loan)
        """
        items = []
        
        try:
            with open(self.filepath, 'r', newline='') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header row
                for row in reader:
                    items.append(self.model_class.from_csv_row(row))
        except FileNotFoundError:
            # Return empty list if file doesn't exist
            pass
        
        return items
    
    def save_all(self, items: List[T]) -> None:
        """
        Save all items to the CSV file.
        
        Args:
            items: List of model instances to save
        """
        # Create header row based on model class
        if self.model_class == Book:
            header = ['ISBN', 'Title', 'Author', 'CopiesTotal', 'CopiesAvailable']
        elif self.model_class == Member:
            header = ['MemberID', 'Name', 'PasswordHash', 'Email', 'JoinDate']
        elif self.model_class == Loan:
            header = ['LoanID', 'MemberID', 'ISBN', 'IssueDate', 'DueDate', 'ReturnDate']
        else:
            raise ValueError(f"Unknown model class: {self.model_class}")
        
        with open(self.filepath, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)
            for item in items:
                writer.writerow(item.to_csv_row())
    
    def add_item(self, item: T) -> None:
        """
        Add a new item to the CSV file.
        
        Args:
            item: Item to add
        """
        items = self.load_all()
        
        # Check for duplicates
        if self.model_class == Book:
            # For books, check by ISBN
            if any(existing.isbn == item.isbn for existing in items):
                raise ValueError(f"Book with ISBN {item.isbn} already exists")
        elif self.model_class == Member:
            # For members, check by member ID
            if any(existing.member_id == item.member_id for existing in items):
                raise ValueError(f"Member with ID {item.member_id} already exists")
        elif self.model_class == Loan:
            # For loans, check by loan ID
            if any(existing.loan_id == item.loan_id for existing in items):
                raise ValueError(f"Loan with ID {item.loan_id} already exists")
        
        items.append(item)
        self.save_all(items)
    
    def update_item(self, item: T) -> None:
        """
        Update an existing item in the CSV file.
        
        Args:
            item: Item to update
        """
        items = self.load_all()
        updated = False
        
        for i, existing in enumerate(items):
            if self.model_class == Book and existing.isbn == item.isbn:
                items[i] = item
                updated = True
                break
            elif self.model_class == Member and existing.member_id == item.member_id:
                items[i] = item
                updated = True
                break
            elif self.model_class == Loan and existing.loan_id == item.loan_id:
                items[i] = item
                updated = True
                break
        
        if not updated:
            raise ValueError(f"Item not found for update: {item}")
        
        self.save_all(items)
    
    def delete_item(self, item_id: str) -> None:
        """
        Delete an item from the CSV file.
        
        Args:
            item_id: ID of the item to delete (ISBN for books, member_id for members, loan_id for loans)
        """
        items = self.load_all()
        original_count = len(items)
        
        if self.model_class == Book:
            items = [item for item in items if item.isbn != item_id]
        elif self.model_class == Member:
            items = [item for item in items if item.member_id != item_id]
        elif self.model_class == Loan:
            items = [item for item in items if item.loan_id != item_id]
        
        if len(items) == original_count:
            raise ValueError(f"Item not found for deletion: {item_id}")
        
        self.save_all(items)
    
    def get_item_by_id(self, item_id: str) -> Optional[T]:
        """
        Get an item by its ID.
        
        Args:
            item_id: ID of the item (ISBN for books, member_id for members, loan_id for loans)
            
        Returns:
            Item if found, None otherwise
        """
        items = self.load_all()
        
        for item in items:
            if self.model_class == Book and item.isbn == item_id:
                return item
            elif self.model_class == Member and item.member_id == item_id:
                return item
            elif self.model_class == Loan and item.loan_id == item_id:
                return item
        
        return None
    
    def search_items(self, **kwargs) -> List[T]:
        """
        Search for items matching the given criteria.
        
        Args:
            **kwargs: Criteria to match (e.g., title='Clean Code')
            
        Returns:
            List of matching items
        """
        items = self.load_all()
        results = []
        
        for item in items:
            match = True
            
            for key, value in kwargs.items():
                if not hasattr(item, key):
                    match = False
                    break
                
                item_value = getattr(item, key)
                
                # Handle case-insensitive string search
                if isinstance(item_value, str) and isinstance(value, str):
                    if value.lower() not in item_value.lower():
                        match = False
                        break
                # Handle exact match for other types
                elif item_value != value:
                    match = False
                    break
            
            if match:
                results.append(item)
        
        return results


class BookStorage(Storage[Book]):
    """Storage class for Book models."""
    
    def __init__(self, data_dir: str):
        """Initialize book storage."""
        super().__init__(data_dir, 'books.csv', Book)
    
    def search_by_title_or_author(self, keyword: str) -> List[Book]:
        """
        Search for books by title or author.
        
        Args:
            keyword: Search keyword
            
        Returns:
            List of matching books
        """
        books = self.load_all()
        results = []
        
        # Binary search would be more efficient for large datasets
        # But for simplicity, we'll use a simple linear search
        for book in books:
            if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower():
                results.append(book)
        
        return results


class MemberStorage(Storage[Member]):
    """Storage class for Member models."""
    
    def __init__(self, data_dir: str):
        """Initialize member storage."""
        super().__init__(data_dir, 'members.csv', Member)
    
    def get_member_by_email(self, email: str) -> Optional[Member]:
        """
        Get a member by email.
        
        Args:
            email: Email to search for
            
        Returns:
            Member if found, None otherwise
        """
        members = self.load_all()
        
        for member in members:
            if member.email.lower() == email.lower():
                return member
        
        return None


class LoanStorage(Storage[Loan]):
    """Storage class for Loan models."""
    
    def __init__(self, data_dir: str):
        """Initialize loan storage."""
        super().__init__(data_dir, 'loans.csv', Loan)
    
    def get_active_loans_for_member(self, member_id: str) -> List[Loan]:
        """
        Get all active loans for a member.
        
        Args:
            member_id: ID of the member
            
        Returns:
            List of active loans
        """
        loans = self.load_all()
        return [loan for loan in loans if loan.member_id == member_id and not loan.return_date]
    
    def get_overdue_loans(self) -> List[Loan]:
        """
        Get all overdue loans.
        
        Returns:
            List of overdue loans
        """
        loans = self.load_all()
        today = datetime.now()
        return [loan for loan in loans if not loan.return_date and loan.due_date < today]
    
    def get_loans_for_book(self, isbn: str) -> List[Loan]:
        """
        Get all loans for a book.
        
        Args:
            isbn: ISBN of the book
            
        Returns:
            List of loans for the book
        """
        loans = self.load_all()
        return [loan for loan in loans if loan.isbn == isbn]
    
    def generate_loan_id(self) -> str:
        """
        Generate a new unique loan ID.
        
        Returns:
            New loan ID
        """
        loans = self.load_all()
        if not loans:
            return "1"
        
        # Get the highest loan ID and increment by 1
        max_id = max(int(loan.loan_id) for loan in loans)
        return str(max_id + 1)
