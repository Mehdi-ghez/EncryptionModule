import tkinter as tk
from tkinter import ttk, messagebox
import time
from DB.users_db import verify_credentials, get_user_list

class LoginWindow:
    def __init__(self, master, app_state):
        self.master = master
        self.app_state = app_state
        
        # Create window
        self.window = tk.Toplevel(master)
        self.window.title("Login - Secure Cracker")
        self.window.geometry("400x300")
        self.window.configure(bg='#2c3e50')
        
        # Initialize variables
        self.cracker_window = None
        self.countdown_id = None
        self.remaining_time = 0
        
        # Build UI
        self._setup_ui()
        
    def _setup_ui(self):
        # Title
        title_label = tk.Label(self.window, text="Password Cracker - Login",
                             bg='#2c3e50', fg='white',
                             font=('Helvetica', 16, 'bold'))
        title_label.pack(pady=20)

        # Main frame
        main_frame = tk.Frame(self.window, bg='#2c3e50')
        main_frame.pack(pady=10)

        # Username section
        username_label = tk.Label(main_frame, text="Username:", bg='#2c3e50', fg='white')
        self.username_var = tk.StringVar()
        self.username_input = ttk.Combobox(main_frame, width=27, 
                                         textvariable=self.username_var,
                                         values=get_user_list())
        self.username_input.set("Select user")
        
        # Password section
        password_frame = tk.Frame(main_frame, bg='#2c3e50')
        password_label = tk.Label(password_frame, text="Password:", bg='#2c3e50', fg='white')
        self.password_input = ttk.Entry(password_frame, width=30, show="*")
        
        # Add show/hide password button
        def toggle_password():
            if self.password_input.cget('show') == '*':
                self.password_input.config(show='')
                show_password_btn.config(text='Hide')
            else:
                self.password_input.config(show='*')
                show_password_btn.config(text='Show')

        show_password_btn = tk.Button(password_frame, text="Show", command=toggle_password)
        
        # Pack username and password sections with proper spacing
        username_label.grid(row=0, column=0, pady=5, padx=5, sticky='e')
        self.username_input.grid(row=0, column=1, pady=5, padx=5)
        password_frame.grid(row=1, column=0, pady=5, padx=5, columnspan=2, sticky='w')
        password_label.pack(side=tk.LEFT, padx=5)
        self.password_input.pack(side=tk.LEFT, padx=5)
        show_password_btn.pack(side=tk.LEFT, padx=5)

        # Buttons frame
        buttons_frame = tk.Frame(self.window, bg='#2c3e50')
        buttons_frame.pack(pady=20)
        
        # Login button
        self.login_button = tk.Button(buttons_frame, text="Login",
                                    bg='#2ecc71', fg='white',
                                    width=15, height=1,
                                    command=self.login)
        self.login_button.pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.window, text="Please login to continue",
                                   bg='#2c3e50', fg='white',
                                   wraplength=300)
        self.status_label.pack(pady=10)

        # Bind Enter key to login
        self.window.bind('<Return>', lambda e: self.login())

    def set_cracker_window(self, cracker_window):
        """Set reference to cracker window for communication"""
        self.cracker_window = cracker_window
    
    def login(self):
        """Handle login attempt"""
        if self.app_state['is_login_locked']:
            self.status_label.config(text="Login is locked. Please wait.", fg='red')
            return
            
        username = self.username_var.get()
        password = self.password_input.get()
        
        if not username or username == "Select user":
            self.status_label.config(text="Please select a username", fg='orange')
            return
            
        if not password:
            self.status_label.config(text="Please enter a password", fg='orange')
            return
        
        if verify_credentials(username, password):
            self.status_label.config(text="Login successful!", fg='green')
        else:
            self.status_label.config(text="Invalid credentials!", fg='red')
            self.password_input.delete(0, tk.END)
            self.password_input.focus()

    def lock_login(self, duration=30):
        """Lock the login window for the specified duration"""
        print(f"LoginWindow: Locking login for {duration} seconds")
        self.app_state['is_login_locked'] = True
        self.remaining_time = duration
        
        # Disable login inputs
        self.username_input.config(state='disabled')
        self.password_input.config(state='disabled')
        self.login_button.config(state='disabled')
        
        # Start countdown
        if self.countdown_id:
            self.window.after_cancel(self.countdown_id)
        self._update_countdown()
    
    def _update_countdown(self):
        """Update the countdown timer display"""
        if self.remaining_time <= 0:
            self.unlock_login()
            return
            
        self.status_label.config(
            text=f"Login locked - Please wait {self.remaining_time} seconds",
            fg='red'
        )
        self.remaining_time -= 1
        self.countdown_id = self.window.after(1000, self._update_countdown)
    
    def unlock_login(self):
        """Unlock the login window"""
        print("LoginWindow: Unlocking login")
        self.app_state['is_login_locked'] = False
        
        # Re-enable login inputs
        self.username_input.config(state='normal')
        self.password_input.config(state='normal')
        self.login_button.config(state='normal')
        
        # Update status
        self.status_label.config(text="Login unlocked - You may try again", fg='green')
        
        # Cancel any remaining countdown
        if self.countdown_id:
            self.window.after_cancel(self.countdown_id)
            self.countdown_id = None
