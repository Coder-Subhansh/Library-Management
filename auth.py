#!/usr/bin/env python3
# auth.py
"""
Authentication module for the Library Management System.
Handles user registration, login, and session management.
"""

import re
from typing import Dict, Optional, Tuple, Literal
from datetime import datetime
from models import Member
from storage import MemberStorage

# Global session dictionary to store the currently logged-in user
session: Dict[str, str] = {}


def validate_password(password: str) -> bool:
    """
    Validate a password.
    
    Args:
        password: Password to validate
        
    Returns:
        True if password is valid, False otherwise
    """
    # Password must be at least 8 characters long
    # and contain at least one uppercase letter, one lowercase letter, and one digit
    return (len(password) >= 8 and
            re.search(r'[A-Z]', password) and
            re.search(r'[a-z]', password) and
            re.search(r'[0-9]', password))


def validate_email(email: str) -> bool:
    """
    Validate an email address.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    # Simple email validation using regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def register_member(data_dir: str, name: str, email: str, password: str, confirm_password: str) -> Tuple[bool, str]:
    """
    Register a new member.
    
    Args:
        data_dir: Directory containing CSV files
        name: Name of the member
        email: Email of the member
        password: Password of the member
        confirm_password: Password confirmation
        
    Returns:
        Tuple (success, message)
    """
    # Check if passwords match
    if password != confirm_password:
        return False, "Passwords do not match"
    
    # Validate password
    if not validate_password(password):
        return False, "Password must be at least 8 characters long and contain uppercase, lowercase, and digit"
    
    # Validate email
    if not validate_email(email):
        return False, "Invalid email format"
    
    # Check if email is already registered
    member_storage = MemberStorage(data_dir)
    if member_storage.get_member_by_email(email):
        return False, "Email is already registered"
    
    # Generate a new member ID
    members = member_storage.load_all()
    if not members:
        member_id = "1001"  # Start with 1001 if no members exist
    else:
        # Get the highest member ID and increment by 1
        max_id = max(int(member.member_id) for member in members)
        member_id = str(max_id + 1)
    
    # Hash the password
    password_hash = Member.hash_password(password)
    
    # Create a new member
    new_member = Member(
        member_id=member_id,
        name=name,
        password_hash=password_hash,
        email=email,
        join_date=datetime.now()
    )
    
    # Add the member to the storage
    try:
        member_storage.add_item(new_member)
        return True, f"Member registered successfully. Your member ID is {member_id}."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login(data_dir: str, id_or_email: str, password: str, role: Literal['librarian', 'member'] = 'member') -> Tuple[bool, str]:
    """
    Login a user.
    
    Args:
        data_dir: Directory containing CSV files
        id_or_email: Member ID or email
        password: Password
        role: Role of the user (librarian or member)
        
    Returns:
        Tuple (success, message)
    """
    # For librarian login, use hardcoded credentials
    if role == 'librarian':
        # In a real system, this would be stored securely
        # and the password would be hashed
        librarian_id = "admin"
        librarian_password = "Admin123"
        
        if id_or_email == librarian_id and password == librarian_password:
            session['user_id'] = librarian_id
            session['role'] = 'librarian'
            return True, "Logged in as librarian"
        else:
            return False, "Invalid librarian credentials"
    
    # For member login
    member_storage = MemberStorage(data_dir)
    member = None
    
    # Check if input is an email or member ID
    if '@' in id_or_email:
        member = member_storage.get_member_by_email(id_or_email)
    else:
        member = member_storage.get_item_by_id(id_or_email)
    
    if not member:
        return False, "Member not found"
    
    if member.verify_password(password):
        session['user_id'] = member.member_id
        session['role'] = 'member'
        session['name'] = member.name
        return True, f"Logged in as {member.name}"
    else:
        return False, "Invalid password"


def logout() -> None:
    """Log out the current user."""
    session.clear()


def is_logged_in() -> bool:
    """Check if a user is logged in."""
    return 'user_id' in session


def get_current_user_id() -> Optional[str]:
    """Get the ID of the currently logged-in user."""
    return session.get('user_id')


def get_current_user_role() -> Optional[str]:
    """Get the role of the currently logged-in user."""
    return session.get('role')


def get_current_user_name() -> Optional[str]:
    """Get the name of the currently logged-in user."""
    return session.get('name')


def require_login(role: Optional[str] = None) -> Tuple[bool, str]:
    """
    Check if the current user is logged in and has the required role.
    
    Args:
        role: Required role (librarian or member)
        
    Returns:
        Tuple (success, message)
    """
    if not is_logged_in():
        return False, "You must be logged in to access this feature"
    
    if role and get_current_user_role() != role:
        return False, f"You must be a {role} to access this feature"
    
    return True, "Access granted"
