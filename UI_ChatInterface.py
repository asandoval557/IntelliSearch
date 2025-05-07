import tkinter as tk
from tkinter import messagebox
import NLP
import DataBases
import ComplianceSecurity
import Main

# Global context
currentUser = None

def run_chat():
    """Entry point, show login screen first, then chat interface on successful login."""
    show_login()
    tk.mainloop()

def show_login():
    """Create and display the login screen."""
    login_win = tk.Toplevel()
    login_win.title("Login")
    # initial window size
    login_win.geometry("300x200")
    # allow user to resize
    login_win.resizable(True, True)
    # prevent the user from shrinking the window beyond the initial window size
    login_win.minsize(300, 200)

    tk.Label(login_win, text="Username:").pack(pady=(20,5))
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Password:").pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    def attempt_login():
        user = username_entry.get().strip()
        password = password_entry.get().strip()
        if not user or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password.")
            return
        if ComplianceSecurity.is_authorized (user, "login"):
            global current_user
            current_user = user
            login_win.destroy()
            show_chat_interface()
        else:
            messagebox.showerror("Unathorized", "Invalid credentials or insufficient permissions.")
    tk.Button(login_win, text="Login", command=attempt_login).pack(pady=20)

