import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import time
import string
import itertools
import threading
from DB.users_db import USERS, get_user_list

class CrackerWindow:
    def __init__(self, master, app_state):
        self.master = master
        self.app_state = app_state
        
        # Create window
        self.window = tk.Toplevel(master)
        self.window.title("Password Cracker Tool")
        self.window.geometry("800x600")
        self.window.configure(bg='#2c3e50')
        
        # Initialize variables
        self.login_window = None
        self.dictionary = []
        self.active_password_type = None
        self.attack_running = False
        self.stop_attack = False
        self.user_attempt_count = 0
        self.test_attempt_count = 0
        self.prevention_enabled = False
        
        # Build UI
        self._setup_ui()
        
    def _setup_ui(self):
        # Create frames
        top_frame = tk.Frame(self.window, bg='#2c3e50')
        left_frame = tk.Frame(self.window, bg='#2c3e50')
        right_frame = tk.Frame(self.window, bg='#2c3e50')
        
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Mode selection
        self.mode_var = tk.StringVar(value="test")
        tk.Label(top_frame, text="Mode:", bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(top_frame, text="Test Mode", variable=self.mode_var, value="test",
                      bg='#2c3e50', fg='white', selectcolor='#2c3e50',
                      command=self._update_mode).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(top_frame, text="User Mode", variable=self.mode_var, value="user",
                      bg='#2c3e50', fg='white', selectcolor='#2c3e50',
                      command=self._update_mode).pack(side=tk.LEFT, padx=10)
        
        # User selection frame (initially hidden)
        self.user_frame = tk.Frame(top_frame, bg='#2c3e50')
        tk.Label(self.user_frame, text="Target User:", bg='#2c3e50', fg='white').pack(side=tk.LEFT, padx=5)
        self.user_var = tk.StringVar()
        self.user_select = ttk.Combobox(self.user_frame, textvariable=self.user_var, width=20,
                                      state='readonly', values=get_user_list())
        self.user_select.pack(side=tk.LEFT, padx=5)
        self.user_select.bind('<<ComboboxSelected>>', self._on_user_selected)
        
        # Left frame - Password Types
        tk.Label(left_frame, text="Password Types:", bg='#2c3e50', fg='white',
               font=('Helvetica', 12, 'bold')).pack(pady=5)
        
        type_frame = tk.Frame(left_frame, bg='#2c3e50')
        type_frame.pack(pady=10, fill=tk.X)
        
        self.password_types = {
            "Binary (3 chars)": {"charset": "01", "attack": "Dictionary"},
            "Numeric (5 chars)": {"charset": string.digits, "attack": "Dictionary"},
            "Alphanumeric (5 chars)": {"charset": string.ascii_letters + string.digits + string.punctuation, 
                                      "attack": "Brute Force"}
        }
        
        self.type_buttons = {}
        for type_name in self.password_types.keys():
            btn = tk.Button(type_frame, text=type_name, bg='#1dd1a1', fg='white',
                          relief="raised", height=2,
                          command=lambda t=type_name: self._select_password_type(t))
            btn.pack(fill=tk.X, pady=5)
            self.type_buttons[type_name] = btn
        
        # Prevention button
        self.prevention_button = tk.Button(left_frame, text="Enable Attack Prevention", 
                                        bg='#9b59b6', fg='white', height=2,
                                        command=self._toggle_prevention)
        self.prevention_button.pack(fill=tk.X, pady=20)
        
        # Right frame - Controls
        tk.Label(right_frame, text="Password:", bg='#2c3e50', fg='white').pack(pady=5)
        self.password_input = ttk.Entry(right_frame, width=40)
        self.password_input.pack(pady=5)
        
        # Control buttons
        btn_frame = tk.Frame(right_frame, bg='#2c3e50')
        btn_frame.pack(pady=10, fill=tk.X)
        
        # Add validate button
        self.validate_button = tk.Button(btn_frame, text="Validate",
                                   bg='#2ecc71', fg='white',
                                   command=self._validate_password)
        self.validate_button.pack(side=tk.LEFT, padx=5)
        
        self.load_dict_button = tk.Button(btn_frame, text="Load Dictionary",
                                       bg='#3498db', fg='white',
                                       command=self._load_dictionary)
        self.load_dict_button.pack(side=tk.LEFT, padx=5)
        
        self.start_button = tk.Button(btn_frame, text="Start Attack",
                                    bg='#e74c3c', fg='white',
                                    command=self._start_attack)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(btn_frame, text="Stop Attack",
                                   bg='#f39c12', fg='white',
                                   command=self._stop_attack)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Status section
        status_frame = tk.Frame(right_frame, bg='#2c3e50')
        status_frame.pack(pady=20, fill=tk.X)
        
        tk.Label(status_frame, text="Status:", bg='#2c3e50', fg='white').pack(anchor='w')
        self.status_text = tk.Label(status_frame, text="Select a password type to begin",
                                 bg='#2c3e50', fg='white', wraplength=300,
                                 justify=tk.LEFT, height=4)
        self.status_text.pack(fill=tk.X, pady=5)
        
        # Progress bar
        tk.Label(right_frame, text="Progress:", bg='#2c3e50', fg='white').pack(anchor='w')
        self.progress_bar = ttk.Progressbar(right_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Time display
        self.time_label = tk.Label(right_frame, text="Time: 0.00s", bg='#2c3e50', fg='white')
        self.time_label.pack(anchor='w', pady=5)
        
        # Attempt counter (only visible when prevention enabled)
        self.attempts_label = tk.Label(right_frame, 
                                    text="Attempts: 0/3", 
                                    bg='#2c3e50', fg='white')
        # Only show when prevention is enabled
        if self.prevention_enabled:
            self.attempts_label.pack(anchor='w', pady=5)
    
    def set_login_window(self, login_window):
        """Set reference to login window for communication"""
        self.login_window = login_window
    
    def _update_mode(self):
        """Handle mode switching between test and user modes"""
        mode = self.mode_var.get()
        if mode == "user":
            self.user_frame.pack(side=tk.RIGHT, padx=10)
            self.password_input.config(state='disabled')
            self.validate_button.config(state='disabled')  # Disable validate button in user mode
            if self.prevention_enabled:
                self.status_text.config(text="Warning: Prevention is enabled. Login will lock after 3 failed attempts.", fg="orange")
            self.attempts_label.config(text=f"Attempts: {self.user_attempt_count}/{self.app_state['max_attempts']}")
        else:
            self.user_frame.pack_forget()
            self.password_input.config(state='normal')
            self.validate_button.config(state='normal')  # Enable validate button in test mode
            self.status_text.config(text="Test mode: Enter a password to crack", fg="white")
            self.attempts_label.config(text=f"Attempts: {self.test_attempt_count}/{self.app_state['max_attempts']}")
    
    def _on_user_selected(self, event=None):
        """Handle user selection in user mode"""
        username = self.user_var.get()
        if not username:
            return
            
        # Auto-select password type based on username
        user_type = username.split()[1].lower()
        for type_name in self.password_types:
            if user_type in type_name.lower():
                self._select_password_type(type_name)
                break
                
        self.status_text.config(text=f"Selected user: {username}\nReady to crack password", fg="white")
    
    def _select_password_type(self, password_type):
        """Select a password type and update UI"""
        # Reset previous selection
        if self.active_password_type:
            self.type_buttons[self.active_password_type].config(relief="raised")
            
        # Set new selection
        self.active_password_type = password_type
        self.type_buttons[password_type].config(relief="sunken")
        
        # Update status
        attack_type = self.password_types[password_type]["attack"]
        self.status_text.config(text=f"Selected: {password_type}\nAttack type: {attack_type}", fg="white")
    
    def _toggle_prevention(self):
        """Toggle attack prevention on/off"""
        self.prevention_enabled = not self.prevention_enabled
        
        if self.prevention_enabled:
            self.prevention_button.config(text="Disable Attack Prevention", relief="sunken", bg='#8e44ad')
            self.status_text.config(text="Attack prevention enabled (3 attempts max)", fg="white")
            self.user_attempt_count = 0
            self.test_attempt_count = 0
            mode = self.mode_var.get()
            if mode == "user":
                self.attempts_label.config(text=f"Attempts: {self.user_attempt_count}/{self.app_state['max_attempts']}")
            else:
                self.attempts_label.config(text=f"Attempts: {self.test_attempt_count}/{self.app_state['max_attempts']}")
            self.attempts_label.pack(anchor='w', pady=5)  # Show attempts label
        else:
            self.prevention_button.config(text="Enable Attack Prevention", relief="raised", bg='#9b59b6')
            self.status_text.config(text="Attack prevention disabled", fg="white")
            self.attempts_label.pack_forget()  # Hide attempts label
            
            # If login window is locked, unlock it
            if self.app_state['is_login_locked'] and self.login_window:
                self.login_window.unlock_login()
    
    def _load_dictionary(self):
        """Load password dictionary from file"""
        dict_file = filedialog.askopenfilename(
            title="Select Dictionary File",
            filetypes=[("Text files", "*.txt")]
        )
        
        if not dict_file:
            return
            
        try:
            with open(dict_file, "r", encoding="utf-8", errors="ignore") as file:
                self.dictionary = [line.strip() for line in file]
            self.status_text.config(text=f"Dictionary loaded: {len(self.dictionary)} passwords", fg="green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dictionary: {e}")
            self.status_text.config(text=f"Failed to load dictionary: {e}", fg="red")
    
    def _start_attack(self):
        """Start password cracking attack"""
        if self.attack_running:
            messagebox.showinfo("Info", "An attack is already running")
            return
            
        if not self.active_password_type:
            messagebox.showwarning("Warning", "Please select a password type first")
            return
            
        attack_type = self.password_types[self.active_password_type]["attack"]
        if attack_type == "Dictionary" and not self.dictionary:
            messagebox.showwarning("Warning", "Please load a dictionary first")
            return
        
        mode = self.mode_var.get()
        
        # Check prevention in both modes if enabled
        if self.prevention_enabled:
            if mode == "user":
                if self.user_attempt_count >= self.app_state['max_attempts']:
                    self.status_text.config(text="Maximum attempts reached. Prevention active.", fg="red")
                    if self.login_window:
                        self.login_window.lock_login(self.app_state['lock_duration'])
                    return
            else:  # test mode
                if self.test_attempt_count >= self.app_state['max_attempts']:
                    self.status_text.config(text="Maximum attempts reached. Prevention active.", fg="red")
                    return
        
        # Get target password
        if mode == "user":
            username = self.user_var.get()
            if not username:
                messagebox.showwarning("Warning", "Please select a target user")
                return
            password = USERS[username]["password"]
            self.password_input.delete(0, tk.END)
            self.password_input.insert(0, "********")  # Hide real password
        else:
            password = self.password_input.get()
            if not password:
                messagebox.showwarning("Warning", "Please enter a password to crack")
                return
        
        # Reset status
        self.stop_attack = False
        self.attack_running = True
        self.progress_bar['value'] = 0
        self.status_text.config(text="Starting attack...", fg="white")
        
        # Start attack in separate thread
        threading.Thread(
            target=self._run_attack,
            args=(password, attack_type, mode),
            daemon=True
        ).start()
    
    def _stop_attack(self):
        """Stop the running attack"""
        if not self.attack_running:
            return
            
        self.stop_attack = True
        self.status_text.config(text="Stopping attack...", fg="white")
    
    def _run_attack(self, password, attack_type, mode):
        """Run the actual password cracking attack"""
        start_time = time.time()
        
        try:
            if attack_type == "Brute Force":
                self._brute_force_attack(password, mode)
            else:
                self._dictionary_attack(password, mode)
        finally:
            elapsed_time = time.time() - start_time
            self.window.after(0, lambda: self.time_label.config(text=f"Time: {elapsed_time:.2f}s"))
            self.attack_running = False
    
    def _increment_attempt_count(self, mode):
        """Increment attempt count based on mode and check limits"""
        if not self.prevention_enabled:
            return False
            
        if mode == "user":
            self.user_attempt_count += 1
            count = self.user_attempt_count
            self.window.after(0, lambda: self.attempts_label.config(
                text=f"Attempts: {count}/{self.app_state['max_attempts']}"))
            
            # Check if reached max attempts
            if count >= self.app_state['max_attempts']:
                self.window.after(0, lambda: self.status_text.config(
                    text="Maximum attempts reached! Login window locked.", fg="red"))
                if self.login_window:
                    self.login_window.lock_login(self.app_state['lock_duration'])
                return True
        else:  # test mode
            self.test_attempt_count += 1
            count = self.test_attempt_count
            self.window.after(0, lambda: self.attempts_label.config(
                text=f"Attempts: {count}/{self.app_state['max_attempts']}"))
            
            # Check if reached max attempts
            if count >= self.app_state['max_attempts']:
                self.window.after(0, lambda: self.status_text.config(
                    text="Maximum attempts reached in test mode.", fg="red"))
                return True
                
        return False
    
    def _brute_force_attack(self, password, mode):
        """Run brute force attack"""
        charset = self.password_types[self.active_password_type]["charset"]
        password_length = len(password)
        total_combinations = len(charset) ** password_length
        combinations = itertools.product(charset, repeat=password_length)
        
        for i, attempt in enumerate(combinations):
            if self.stop_attack:
                self.window.after(0, lambda: self.status_text.config(
                    text="Attack stopped by user", fg="orange"))
                return
                
            current = ''.join(attempt)
            
            # Count this as an attempt
            if self._increment_attempt_count(mode):
                return  # Stop if max attempts reached
            
            # Update progress every 1000 attempts
            if i % 1000 == 0:
                progress = min(100, (i / total_combinations) * 100)
                self.window.after(0, lambda p=progress: self.progress_bar.config(value=p))
                self.window.after(0, lambda c=current, idx=i: self.status_text.config(
                    text=f"Trying: {c}\nAttempts: {idx:,}\nProgress: {progress:.2f}%", fg="white"))
            
            # Check if password found
            if current == password:
                self.window.after(0, lambda c=current, idx=i: self.status_text.config(
                    text=f"Password cracked!\nPassword: {c}\nAttempts: {idx+1:,}", fg="green"))
                return
        
        # If we got here, password not found
        self.window.after(0, lambda: self.status_text.config(
            text="Password not found after exhausting all combinations", fg="red"))
    
    def _dictionary_attack(self, password, mode):
        """Run dictionary attack"""
        total_words = len(self.dictionary)
        
        for i, word in enumerate(self.dictionary):
            if self.stop_attack:
                self.window.after(0, lambda: self.status_text.config(
                    text="Attack stopped by user", fg="orange"))
                return
            
            # Count this as an attempt
            if self._increment_attempt_count(mode):
                return  # Stop if max attempts reached
            
            # Update progress every 100 words
            if i % 100 == 0:
                progress = min(100, (i / total_words) * 100)
                self.window.after(0, lambda p=progress: self.progress_bar.config(value=p))
                self.window.after(0, lambda w=word, idx=i: self.status_text.config(
                    text=f"Trying: {w}\nWords tested: {idx:,}\nProgress: {progress:.2f}%", fg="white"))
            
            # Check if password found
            if word == password:
                self.window.after(0, lambda w=word, idx=i: self.status_text.config(
                    text=f"Password found!\nPassword: {w}\nAttempts: {idx+1:,}", fg="green"))
                return
        
        # If we got here, password not found in dictionary
        self.window.after(0, lambda: self.status_text.config(
            text=f"Password not found in dictionary ({total_words:,} words checked)", fg="red"))

    def _validate_password(self):
        """Validate the password based on the selected password type"""
        if self.mode_var.get() != "test":
            self.status_text.config(text="Validation only available in Test Mode")
            return
            
        password = self.password_input.get()
        
        if not self.active_password_type:
            self.status_text.config(text="Please select a password type first")
            return
        
        # Validate based on password type
        if "Binary" in self.active_password_type:
            if len(password) == 3 and all(c in "01" for c in password):
                self.status_text.config(text="Valid binary password", fg="green")
            else:
                self.status_text.config(text="Invalid binary password\nMust be 3 characters of 0 or 1", fg="red")
        
        elif "Numeric" in self.active_password_type:
            if len(password) == 5 and password.isdigit():
                self.status_text.config(text="Valid numeric password", fg="green")
            else:
                self.status_text.config(text="Invalid numeric password\nMust be 5 digits", fg="red")
        
        elif "Alphanumeric" in self.active_password_type:
            if len(password) == 5:
                self.status_text.config(text="Valid alphanumeric password", fg="green")
            else:
                self.status_text.config(text="Invalid alphanumeric password\nMust be 5 characters", fg="red")
