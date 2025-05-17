#!/usr/bin/env python3
# models.py
"""
Data models for the Library Management System.
Contains the Book, Member, and Loan classes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
import re


@dataclass
class Book:
    """Represents a book in the library."""
    isbn: str
    title: str
    author: str
    copies_total: int
    copies_available: int

    def __post_init__(self):
        """Validate book data after initialization."""
        # Convert string fields to integers
        if isinstance(self.copies_total, str):
            self.copies_total = int(self.copies_total)
        if isinstance(self.copies_available, str):
            self.copies_available = int(self.copies_available)
        
        # Validate ISBN format (simple validation)
        if not re.match(r'^\d{10}(\d{3})?$', self.isbn):
            raise ValueError(f"Invalid ISBN format: {self.isbn}")
        
        # Validate number of copies
        if self.copies_total < 0:
            raise ValueError(f"Total copies cannot be negative: {self.copies_total}")
        if self.copies_available < 0:
            raise ValueError(f"Available copies cannot be negative: {self.copies_available}")
        if self.copies_available > self.copies_total:
            raise ValueError(f"Available copies ({self.copies_available}) cannot exceed total copies ({self.copies_total})")
    
    def to_csv_row(self) -> list:
        """Convert book to CSV row."""
        return [self.isbn, self.title, self.author, str(self.copies_total), str(self.copies_available)]
    
    @classmethod
    def from_csv_row(cls, row: list) -> 'Book':
        """Create a Book instance from a CSV row."""
        if len(row) != 5:
            raise ValueError(f"Invalid book CSV row: {row}")
        return cls(
            isbn=row[0],
            title=row[1],
            author=row[2],
            copies_total=int(row[3]),
            copies_available=int(row[4])
        )


@dataclass
class Member:
    """Represents a library member."""
    member_id: str
    name: str
    password_hash: str
    email: str
    join_date: datetime
    
    def __post_init__(self):
        """Validate member data after initialization."""
        # Convert string date to datetime if needed
        if isinstance(self.join_date, str):
            self.join_date = datetime.strptime(self.join_date, "%Y-%m-%d")
        
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.email):
            raise ValueError(f"Invalid email format: {self.email}")
    
    def to_csv_row(self) -> list:
        """Convert member to CSV row."""
        return [
            self.member_id,
            self.name,
            self.password_hash,
            self.email,
            self.join_date.strftime("%Y-%m-%d")
        ]
    
    @classmethod
    def from_csv_row(cls, row: list) -> 'Member':
        """Create a Member instance from a CSV row."""
        if len(row) != 5:
            raise ValueError(f"Invalid member CSV row: {row}")
        return cls(
            member_id=row[0],
            name=row[1],
            password_hash=row[2],
            email=row[3],
            join_date=row[4]
        )
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))


@dataclass
class Loan:
    """Represents a book loan."""
    loan_id: str
    member_id: str
    isbn: str
    issue_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate loan data after initialization."""
        # Convert string dates to datetime objects if needed
        if isinstance(self.issue_date, str):
            self.issue_date = datetime.strptime(self.issue_date, "%Y-%m-%d")
        if isinstance(self.due_date, str):
            self.due_date = datetime.strptime(self.due_date, "%Y-%m-%d")
        if isinstance(self.return_date, str) and self.return_date:
            self.return_date = datetime.strptime(self.return_date, "%Y-%m-%d")
    
    def to_csv_row(self) -> list:
        """Convert loan to CSV row."""
        return [
            self.loan_id,
            self.member_id,
            self.isbn,
            self.issue_date.strftime("%Y-%m-%d"),
            self.due_date.strftime("%Y-%m-%d"),
            self.return_date.strftime("%Y-%m-%d") if self.return_date else ""
        ]
    
    @classmethod
    def from_csv_row(cls, row: list) -> 'Loan':
        """Create a Loan instance from a CSV row."""
        if len(row) != 6:
            raise ValueError(f"Invalid loan CSV row: {row}")
        return cls(
            loan_id=row[0],
            member_id=row[1],
            isbn=row[2],
            issue_date=row[3],
            due_date=row[4],
            return_date=row[5] if row[5] else None
        )
    
    @classmethod
    def create_new_loan(cls, loan_id: str, member_id: str, isbn: str) -> 'Loan':
        """Create a new loan with the current date and a 14-day due date."""
        issue_date = datetime.now()
        due_date = issue_date + timedelta(days=14)
        return cls(
            loan_id=loan_id,
            member_id=member_id,
            isbn=isbn,
            issue_date=issue_date,
            due_date=due_date
        )
    
    def is_overdue(self) -> bool:
        """Check if the book is overdue."""
        return not self.return_date and datetime.now() > self.due_date
