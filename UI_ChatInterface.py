import tkinter as tk
from tkinter import messagebox
import NLP
import DataBase
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

    # Frame for buttons
    btn_frame = tk.Frame(login_win)
    btn_frame.pack(pady=(10,5))

    # Login button
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
            messagebox.showerror("Unauthorized", "Invalid credentials or insufficient permissions.")

    login_btn = tk.Button(btn_frame, text="Login", command=attempt_login)
    login_btn.pack(side=tk.RIGHT, padx=10)

    # Register button
    def show_register():
        register_win = tk.Toplevel()
        register_win.title("Register New User")
        register_win.geometry("300x300")
        register_win.resizable(True, True)
        register_win.minsize(300, 300)

        tk.Label(register_win, text="New Username:").pack(pady=(20, 5))
        new_user_entry = tk.Entry(register_win)
        new_user_entry.pack(pady=5)

        tk.Label(register_win, text="New Password:").pack(pady=5)
        new_pass_entry = tk.Entry(register_win, show="*")
        new_pass_entry.pack(pady=5)

        tk.Label(register_win, text="Confirm Password:").pack(pady=5)
        confirm_pass_entry = tk.Entry(register_win, show="*")
        confirm_pass_entry.pack(pady=5)

        def attempt_register():
            new_user = new_user_entry.get().strip()
            new_pass = new_pass_entry.get().strip()
            confirm = confirm_pass_entry.get().strip()
            if not new_user or not new_pass or not confirm:
                messagebox.showerror("Registration Failed", "All fields are required.")
                return
            if new_pass != confirm:
                messagebox.showerror("Registration Failed", "Passwords do not match.")
                return
            # Call ComplianceSecurity to register user
            success = ComplianceSecurity.register_user(new_user, new_pass)
            if success:
                messagebox.showinfo("Registration Successful", "You can now log in with your new credentials.")
                register_win.destroy()
            else:
                messagebox.showerror("Registration Failed", "Username may already exist.")

        tk.Button(register_win, text="Register", command=attempt_register).pack(pady=20)

    register_btn = tk.Button(btn_frame, text="Register", command=show_register)
    register_btn.pack(side=tk.LEFT, padx=10)

def show_chat_interface():
    """Build the main chat interface upon successful login."""
    chat_win = tk.Tk()
    chat_win.title(f"Chat - {current_user}")
    # Set initial window size
    chat_win.geometry("500x600")
    # Allow user to resize window
    chat_win.resizable(True, True)
    # Prevent user from shrinking window smaller than initial login screen
    chat_win.minsize(300, 200)

    # Chat history
    frame = tk.Frame(chat_win)
    frame.pack(expand=True, fill=tk.BOTH)
    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    chat_history = tk.Text(frame, wrap = tk.WORD,yscrollcommand=scrollbar.set,state=tk.DISABLED)
    chat_history.pack(expand=True, fill=tk.BOTH)
    scrollbar.config(command=chat_history.yview)

    # Input frame
    input_frame = tk.Frame(chat_win)
    input_frame.pack(fill=tk.X)
    input_field = tk.Entry(input_frame)
    input_field.pack(side=tk.LEFT,expand=True,fill=tk.X,padx=-5,pady=5)
    input_field.focus()
    send_btn = tk.Button(input_frame, text="Send", command=lambda: handle_message(input_field,chat_history))
    send_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    # Bind Enter Key
    input_field.bind("<Return>", lambda event: handle_message(input_field,chat_history))

    # Show welcome prompt
    append_message(chat_history,f"Bot: Welcome {current_user}! How can I assist you today?")

def append_message(widget, message):
    widget.config(state=tk.NORMAL)
    widget.insert(tk.END, message + "")
    widget.config(state=tk.DISABLED)
    widget.see(tk.END)

def handle_message(input_field, chat_history):
    user_msg = input_field.get().strip()
    if not user_msg:
        return
    append_message(chat_history,f"Bot: You {user_msg}!")
    DataBase.log_activity(current_user, user_msg)

    # Check complaince rules against search action
    if not ComplianceSecurity.is_authorized(current_user, "search"):
        bot_resp = "You do not have permission to perform this search."
    else:
        # Parse and query
        filters = NLP.parse_query(user_msg)
        results = DataBase.query_books(filters)
        bot_resp = "Here are some results:"+" "+" ".join(
            [f"- {r[0]} ({r[1]}, {r[2]})" for r in results[:5]]
        ) if results else "Sorry, I couldn't find any matching items."

        append_message(chat_history,f"Bot: {bot_resp}")
        DataBase.log_activity(current_user, bot_resp)