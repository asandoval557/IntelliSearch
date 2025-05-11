# ComplianceSecurity.py
import DataBase

def init():
    # Load user credentials or tokens
    pass

def register_user(username: str, password: str, role: str = None) -> bool:
    """Register a new user. Returns True on success, False if username exists."""
    return DataBase.create_user(username, password, role)

def is_authorized(username: str, action: str, password: str = None) -> bool:
    # Check if the user is allowed to perform the action
    if action == 'login':
        if password is None:
            return False
        return DataBase.verify_user(username, password)
        # For this MVP, any logged-in user can 'search'
    if action == 'search':
        return True
    return False


def alert_unauthorized(username: str, action: str):
    # Log or notify on unauthorized access attempts
    pass