import tkinter as tk
from pickle import FALSE
from tkinter import messagebox, ttk
import NLP
import DataBase
import ComplianceSecurity
import sys

# Global context
current_user = None


def run_chat():
    """Entry point, show login screen first, then chat interface on successful login."""
    root = tk.Tk()
    root.withdraw()
    show_login(root)
    root.mainloop()


def show_login(root):
    """Create and display the login screen."""
    login_win = tk.Toplevel(root)
    login_win.title("Login")
    # initial window size
    login_win.geometry("300x200")
    # allow user to resize
    login_win.resizable(True, True)
    # prevent the user from shrinking the window beyond the initial window size
    login_win.minsize(300, 200)

    # Apply modern styling
    style = ttk.Style()
    style.configure('TButton', font=("Arial", 10), background='#7349cc')
    style.configure('TLabel', font=("Arial", 10))
    style.configure('TEntry', font=("Arial", 10))

    # Center the form with padding
    main_frame = ttk.Frame(login_win, padding=20)
    main_frame.pack(expand=True, fill=tk.BOTH)

    tk.Label(main_frame, text="Username:").pack(pady=(10, 5), anchor='w')
    username_entry = tk.Entry(main_frame, width=30)
    username_entry.pack(pady=5, fill=tk.X)

    tk.Label(main_frame, text="Password:").pack(pady=5, anchor='w')
    password_entry = tk.Entry(main_frame, show="*", width=30)
    password_entry.pack(pady=5, fill=tk.X)

    # Frame for buttons
    btn_frame = tk.Frame(main_frame)
    btn_frame.pack(pady=(10, 5))

    # Login button
    def attempt_login():
        user = username_entry.get().strip()
        password = password_entry.get().strip()
        if not user or not password:
            messagebox.showerror("Login Failed", "Please enter both username and password.")
            return
        if ComplianceSecurity.is_authorized(user, "login", password):
            global current_user
            current_user = user
            login_win.destroy()
            show_chat_interface(root)
        else:
            messagebox.showerror("Unauthorized", "Invalid credentials or insufficient permissions.")

    login_btn = tk.Button(btn_frame, text="Login", command=attempt_login, width=15)
    login_btn.pack(side=tk.LEFT, padx=5)

    # Register button
    def show_register():
        register_win = tk.Toplevel(root)
        register_win.title("Register New User")
        register_win.geometry("300x300")
        register_win.resizable(True, True)
        register_win.minsize(300, 300)

        reg_frame = ttk.Frame(register_win, padding=20)
        reg_frame.pack(expand=True, fill=tk.BOTH)

        tk.Label(reg_frame, text="New Username:").pack(pady=(10, 5), anchor='w')
        new_user_entry = tk.Entry(reg_frame, width=30)
        new_user_entry.pack(pady=5, fill=tk.X)

        tk.Label(reg_frame, text="New Password:").pack(pady=5, anchor='w')
        new_pass_entry = tk.Entry(reg_frame, show="*")
        new_pass_entry.pack(pady=5, fill=tk.X)

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


def show_chat_interface(root):
    """Build the main chat interface upon successful login."""
    chat_win = tk.Toplevel(root)
    chat_win.title(f"Chat - {current_user}")
    # Set initial window size
    chat_win.geometry("500x600")
    # Allow user to resize window
    chat_win.resizable(True, True)
    # Prevent user from shrinking window smaller than initial login screen
    chat_win.minsize(300, 200)
    chat_win.configure(bg='#f0f0f5')

    # Handle window close event for proper exit
    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            root.quit()
            root.destroy()
            sys.exit()

    chat_win.protocol("WM_DELETE_WINDOW", on_closing)

    header_frame = tk.Frame(chat_win, bg="#7349cc", height=50)
    header_frame.pack(fill=tk.X)
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
    chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # Create the frame inside the canvas to hold messages
    messages_frame = tk.Frame(chat_canvas, bg="#f0f0f5")
    chat_canvas.create_window((0, 0), window=messages_frame, anchor='nw', tags="messages_frame")

    def configure_messages_frame(event):
        chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
        chat_canvas.itemconfig("messages_frame", width=chat_canvas.winfo_width())

    messages_frame.bind("<Configure>", configure_messages_frame)
    chat_canvas.bind("<Configure>", configure_messages_frame)

    # Bottom user input area
    input_frame = tk.Frame(chat_win, bg='white', height=60)
    input_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

    # Text input area with rounded corners
    entry_frame = tk.Frame(input_frame, bg='white', bd=1, relief=tk.SOLID)
    entry_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

    input_field = tk.Entry(entry_frame, bd=0, font=('Arial', 10), bg='white')
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
    send_btn = tk.Button(input_frame, text="Send", font=('Arial', 10, 'bold'), bg='#7349cc', fg='white', padx=15,
                         pady=8, activebackground='#5c3ba6', activeforeground='white', command=lambda: handle_message(
            input_field, messages_frame, chat_canvas, chat_win, root))
    send_btn.pack(side=tk.RIGHT)

    # Bind Enter Key
    input_field.bind("<Return>", lambda event: handle_message(input_field, messages_frame, chat_canvas, chat_win, root))

    # Display welcome message and update scroll region properly
    def show_welcome():
        add_bot_message(messages_frame, f"Hello {current_user}! How can I help you?")
        # Force update of the canvas and scroll region
        messages_frame.update_idletasks()
        chat_canvas.update_idletasks()
        chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
        # Make sure the message is visible
        chat_canvas.yview_moveto(0.0)

    # Use after() to ensure the interface is fully rendered first
    chat_win.after(100, show_welcome)

    # Focus on input field
    input_field.focus_set()


def add_bot_message(container, message):
    """Add a message from the bot to the chat"""
    msg_frame = tk.Frame(container, bg="#f0f0f5")
    msg_frame.pack(fill=tk.X, pady=10)

    msg_bubble = tk.Label(msg_frame, text=message, wraplength=250, bg="#273746", fg='white', padx=12, pady=8,
                          relief=tk.FLAT, anchor='w')
    msg_bubble.pack(side=tk.LEFT, padx=10)


def add_user_message(container, message):
    """Add a message from the user to the chat"""
    msg_frame = tk.Frame(container, bg="#f0f0f5")
    msg_frame.pack(fill=tk.X, pady=5)

    msg_bubble = tk.Label(msg_frame, text=message, wraplength=250, justify=tk.RIGHT, bg='#7349cc',
                          fg='white', padx=12, pady=8, relief=tk.FLAT, anchor='e')
    msg_bubble.pack(side=tk.RIGHT, padx=10)


def clear_chat_messages(messages_container, chat_canvas):
    """Clear all messages from the chat interface"""
    # Destroy all child widgets in the messages container
    for widget in messages_container.winfo_children():
        widget.destroy()

    # Update the canvas scroll region
    messages_container.update_idletasks()
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
    chat_canvas.yview_moveto(0.0)


def handle_message(input_field, messages_container, chat_canvas, chat_win, root):
    user_msg = input_field.get().strip()

    # Clear placeholder or empty messages
    if user_msg == "Type your message..." or not user_msg:
        return

    # Display user message
    add_user_message(messages_container, user_msg)
    update_scroll_region(chat_canvas, messages_container)

    # Clear the input field
    input_field.delete(0, tk.END)

    # Log user activity
    if current_user:
        DataBase.log_activity(current_user, user_msg)
    else:
        # Use a default user if current_user is not set
        DataBase.log_activity("guest", user_msg)

    # Process the message and generate response
    if current_user and not ComplianceSecurity.is_authorized(current_user, "search"):
        bot_resp = "You do not have permission to perform this search."
    else:
        # Parse and query
        filters = NLP.extract_filters_from_query(user_msg)

        # Check for clear request
        if filters.get('clear_request'):
            clear_chat_messages(messages_container, chat_canvas)
            bot_resp = "Chat cleared! How can I help you?"
        # Check for exit request
        elif filters.get('exit_request'):
            # Show confirmation dialog
            if messagebox.askyesno("Exit", "Are you sure you want to exit the program?"):
                root.quit()
                root.destroy()
                sys.exit()
            else:
                bot_resp = "Exit cancelled. How can I continue helping you?"
        # Check if user is asking for help
        elif filters.get('help_request'):
            bot_resp = NLP.get_help_message()
        # Check if NLP found no searchable content
        elif filters.get('no_results'):
            bot_resp = "I couldn't understand what you're looking for. Please try searching by genre (like 'fantasy' or 'mystery') or publication year (like '1990s' or 'after 2010'). Type 'what can you do' for more detailed instructions."
        else:
            results = DataBase.query_books(filters)
            if results:
                bot_resp = "Here are some results:\n" + "\n".join(
                    [f"- {r[0]} ({r[1]}, {r[2]})" for r in results[:5]])
            else:
                bot_resp = "No results found matching your criteria."

    # Add bot response with delay and update scroll (only if not clearing or exiting)
    if not filters.get('clear_request') and not (
            filters.get('exit_request') and messagebox.askyesno("Exit", "Are you sure you want to exit the program?")):
        def add_delayed_response():
            add_bot_message(messages_container, bot_resp)
            update_scroll_region(chat_canvas, messages_container)
            # Log the bot response
            if current_user:
                DataBase.log_activity(current_user, bot_resp)

        messages_container.after(500, add_delayed_response)


def update_scroll_region(chat_canvas, message_frame):
    """Update the scroll region to fit within a message"""
    message_frame.update_idletasks()
    chat_canvas.configure(scrollregion=chat_canvas.bbox("all"))
    # Auto scroll to the bottom
    chat_canvas.yview_moveto(1.0)


if __name__ == "__main__":
    # Initialize database before starting the application
    DataBase.init_db()
    run_chat()