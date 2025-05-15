import tkinter as tk
from pickle import FALSE
from tkinter import messagebox, ttk
import NLP
import DataBase
import ComplianceSecurity


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

    # Apply modern styling
    style = ttk.Style()
    style.configure('TButton', font=("Arial", 10), background = '#7349cc')
    style.configure('TLabel', font=("Arial", 10))
    style.configure('TEntry', font=("Arial", 10))

    # Center the form with padding
    main_frame = ttk.Frame(login_win, padding = 20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(main_frame, text="Username:").pack(pady=(10,5), anchor='w')
    username_entry = tk.Entry(main_frame, width=30)
    username_entry.pack(pady=5, fill=tk.X)

    tk.Label(main_frame, text="Password:").pack(pady=5, anchor='w')
    password_entry = tk.Entry(main_frame, show="*", width=30)
    password_entry.pack(pady=5, fill=tk.X)


    # Frame for buttons
    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(pady=(10,5))

    # Login button
    def attempt_login():
        user = username_entry.get().strip()
        password = password_entry.get().strip()
        if not user or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password.")
            return
        if ComplianceSecurity.is_authorized (user, "login", password):
            global current_user
            current_user = user
            login_win.destroy()
            show_chat_interface()
        else:
            messagebox.showerror("Unauthorized", "Invalid credentials or insufficient permissions.")

    login_btn = tk.Button(btn_frame, text="Login", command=attempt_login, width=15)
    login_btn.pack(side=tk.LEFT, padx=5)

    # Register button
    def show_register():
        register_win = tk.Toplevel()
        register_win.title("Register New User")
        register_win.geometry("300x300")
        register_win.resizable(True, True)
        register_win.minsize(300, 300)

        reg_frame = ttk.Frame(register_win, padding = 20)
        reg_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(reg_frame, text="New Username:").pack(pady=(10, 5), anchor='w')
        new_user_entry = tk.Entry(reg_frame, width=30)
        new_user_entry.pack(pady=5, fill=tk.X)

        tk.Label(reg_frame, text="New Password:").pack(pady=5, anchor='w')
        new_pass_entry = tk.Entry(reg_frame, show="*")
        new_pass_entry.pack(pady=5,fill=tk.X)

        tk.Label(reg_frame, text="Confirm Password:").pack(pady=5, anchor='w')
        confirm_pass_entry = tk.Entry(reg_frame, show="*")
        confirm_pass_entry.pack(pady=5, fill=tk.X)

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

        tk.Button(reg_frame, text="Register", command=attempt_register, width=15).pack(pady=20)

    register_btn = tk.Button(btn_frame, text="Register", command=show_register, width=10)
    register_btn.pack(side=tk.LEFT, padx=5)

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
    chat_win.configure(bg='#f0f0f5')

    header_frame = tk.Frame(chat_win, bg="#7349cc", height=50)
    header_frame.pack(fill = tk.X)
    header_frame.pack_propagate(False)

    title_label = tk.Frame(header_frame, bg="#7349cc")
    title_label.pack(expand=True)

    # Main Chat with light gray background
    chat_frame = tk.Frame(chat_win, bg="#f0f0f5")
    chat_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Chat history with modern styling
    history_frame = tk.Frame(chat_frame, bg="#f0f0f5")
    history_frame.pack(expand=True, fill=tk.BOTH)

    # Creating a canvas with scrollbar for smooth scrolling
    chat_canvas = tk.Canvas(history_frame, bg="#f0f0f5", highlightthickness=0)
    scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=chat_canvas.yview)

    # Configure the canvas
    chat_canvas.configure(yscrollcommand=scrollbar.set)
    chat_canvas.pack(side = tk.LEFT, fill = tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    #Create the frame inside the canvas to hold messages
    messages_frame = tk.Frame(chat_canvas, bg="#f0f0f5")
    chat_canvas.create_window((0, 0),window= messages_frame, anchor='nw', tags="messages_frame")

    def configure_messages_frame(event):
        chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
        chat_canvas.itemconfig("messages_frame", width=chat_canvas.winfo_width())

    messages_frame.bind("<Configure>", configure_messages_frame)

    # Bottom user input area
    input_frame = tk.Frame(chat_win, bg='white', height=60)
    input_frame.pack(fill=tk.X, side = tk.BOTTOM, padx=10, pady=10)

    # Text input area with rounded corners
    entry_frame = tk.Frame(input_frame, bg='white', bd=1, relief=tk.SOLID)
    entry_frame.pack(side=tk.LEFT,fill=tk.X, expand=True, padx=(0,10))

    input_field = tk.ENTRY(entry_frame, bd=0, font=('Arial',10), bg='white')
    input_field.pack(fill=tk.X, expand=True, ipady=8, padx=10)
    input_field.insert(0, "Type your message...")

    # Clear the placeholder text
    def clear_placeholder(event):
        if input_field.get() == "Type your message...":
            input_field.delete(0, tk.END)

    # Add placeholder text if empty
    def add_placeholder(event):
        if input_field.get() == "":
            input_field.insert(tk.END, "Type your message...")

    input_field.bind("<FocusIn>", clear_placeholder)
    input_field.bind("<FocusOut>", add_placeholder)

    # Send Button with modern styling
    send_btn = tk.Button(input_frame, text="Send", font=('Arial', 10, 'bold'), bg='#7349cc', fg='white', padx= 15,
                         pady= 8 , activebackground='#5c3ba6', activeforeground='white', command=lambda: handle_message(
                        input_field, messages_frame))
    send_btn.pack(side=tk.RIGHT)



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