import tkinter as tk
import customtkinter as ctk
from main import main
from Modules.caesar_cipher import CaesarCipherApp
from Modules.AffineCipher import AffineCipherApp
from Modules.ShiftCipher import ShiftCipher
from Modules.Mirror import mirror
from Modules.stan import SteganoApp  # Add this import

class CryptoInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Crypto Tools")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')

        # Configure grid weight to center the content
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create a frame to hold the buttons
        button_frame = tk.Frame(self.root, bg='#2c3e50')
        button_frame.grid(row=0, column=0)

        # Create buttons with new colors and commands
        self.crypto_btn = tk.Button(button_frame, text="Cryptography", width=15, height=2,
                                  bg='#1dd1a1', fg='white',
                                  command=self.open_cryptography_interface)
        self.cracking_btn = tk.Button(button_frame, text="Cracking", width=15, height=2,
                                    bg='#1dd1a1', fg='white',
                                    command=self.open_cracking_interface)
        self.stego_btn = tk.Button(button_frame, text="Steganography", width=15, height=2,
                                 bg='#1dd1a1', fg='white',
                                 command=self.open_steganography_interface)

        # Pack buttons with some padding
        self.crypto_btn.pack(pady=10)
        self.cracking_btn.pack(pady=10)
        self.stego_btn.pack(pady=10)

        self.cipher_windows = []  # Add this line to track open windows

    def enable_crypto_button(self):
        """Re-enable the cryptography button"""
        self.crypto_btn.config(state='normal')

    def enable_cracking_button(self):
        """Re-enable the cracking button"""
        self.cracking_btn.config(state='normal')

    def enable_stego_button(self):
        """Re-enable the steganography button"""
        self.stego_btn.config(state='normal')

    def open_cryptography_interface(self):
        """Open the cryptography interface"""
        self.crypto_btn.config(state='disabled')
        # Create frame for buttons in the main window (not a new window)
        crypto_frame = tk.Frame(self.root, bg='#2c3e50')
        crypto_frame.grid(row=1, column=0, pady=20)  # Place below the main buttons

        # Create buttons for each cipher horizontally
        caesar_btn = tk.Button(crypto_frame, text="Caesar Cipher", width=15, height=2,
                             bg='#1dd1a1', fg='white',
                             command=lambda: self.open_cipher_window("Caesar"))
        
        affine_btn = tk.Button(crypto_frame, text="Affine Cipher", width=15, height=2,
                              bg='#1dd1a1', fg='white',
                              command=lambda: self.open_cipher_window("Affine"))
        
        shift_btn = tk.Button(crypto_frame, text="Shift Cipher", width=15, height=2,
                            bg='#1dd1a1', fg='white',
                            command=lambda: self.open_cipher_window("Shift"))
        
        mirror_btn = tk.Button(crypto_frame, text="Mirror Text", width=15, height=2,
                             bg='#1dd1a1', fg='white',
                             command=lambda: self.open_cipher_window("Mirror"))

        # Pack buttons horizontally with padding
        caesar_btn.pack(side='left', padx=10)
        affine_btn.pack(side='left', padx=10)
        shift_btn.pack(side='left', padx=10)
        mirror_btn.pack(side='left', padx=10)

        # Store the frame reference to destroy it later
        self.current_crypto_frame = crypto_frame

    def open_cipher_window(self, cipher_type):
        """Open a cipher window and handle its closure"""
        window = tk.Toplevel(self.root)
        self.cipher_windows.append(window)
        
        if cipher_type == "Caesar":
            CaesarCipherApp(window)
        elif cipher_type == "Affine":
            AffineCipherApp(window)
        elif cipher_type == "Shift":
            self.setup_shift_interface(window)
        elif cipher_type == "Mirror":
            self.setup_mirror_interface(window)

        def on_window_close():
            if window in self.cipher_windows:
                self.cipher_windows.remove(window)
            window.destroy()
            if not self.cipher_windows:  # If no cipher windows are open
                if self.current_crypto_frame:
                    self.current_crypto_frame.destroy()
                    self.current_crypto_frame = None
                self.enable_crypto_button()

        window.protocol("WM_DELETE_WINDOW", on_window_close)

    def setup_shift_interface(self, window):
        """Setup the shift cipher interface"""
        window.title("Shift Cipher")
        window.geometry("900x600")
        
        cipher = ShiftCipher()
        
        # Create main container
        main_frame = ctk.CTkFrame(window)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Input Section
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(pady=20, padx=20, fill="x")

        ctk.CTkLabel(input_frame, text="Enter text to shift:", 
                    font=("Arial", 14)).pack(pady=5)
        
        self.shift_input = ctk.CTkTextbox(input_frame, height=100)
        self.shift_input.pack(pady=5, fill="x")
        
        # Direction Selection
        direction_frame = ctk.CTkFrame(main_frame)
        direction_frame.pack(pady=10)
        
        self.direction_var = tk.StringVar(value="g")
        left_radio = ctk.CTkRadioButton(direction_frame, text="Left (g)", 
                                      variable=self.direction_var, value="g")
        right_radio = ctk.CTkRadioButton(direction_frame, text="Right (d)", 
                                       variable=self.direction_var, value="d")
        
        left_radio.pack(side="left", padx=10)
        right_radio.pack(side="left", padx=10)

        # Process Button
        process_btn = ctk.CTkButton(main_frame, text="Process Shift", 
                                  command=lambda: self.process_shift(cipher))
        process_btn.pack(pady=20)

        # Result Section
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(result_frame, text="Result:", 
                    font=("Arial", 14)).pack(pady=5)
        
        self.shift_result = ctk.CTkTextbox(result_frame, height=100)
        self.shift_result.pack(pady=5, fill="both", expand=True)

    def process_shift(self, cipher):
        """Process text with shift cipher"""
        text = self.shift_input.get("1.0", "end-1c").strip()
        direction = self.direction_var.get()
        if text:
            result = cipher.encrypt(text + direction)
            self.shift_result.delete("1.0", "end")
            if result:
                self.shift_result.insert("1.0", result)

    def setup_mirror_interface(self, window):
        """Setup the mirror interface"""
        window.title("Mirror Text")
        window.geometry("900x600")
        
        # Create main container
        main_frame = ctk.CTkFrame(window)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Input Section
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(input_frame, text="Enter text to mirror:", 
                    font=("Arial", 14)).pack(pady=5)
        
        self.mirror_input = ctk.CTkTextbox(input_frame, height=100)
        self.mirror_input.pack(pady=5, fill="x")

        # Mirror Button
        mirror_btn = ctk.CTkButton(main_frame, text="Mirror Text", 
                                 command=self.process_mirror)
        mirror_btn.pack(pady=20)

        # Result Section
        result_frame = ctk.CTkFrame(main_frame)
        result_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(result_frame, text="Result:", 
                    font=("Arial", 14)).pack(pady=5)
        
        self.mirror_result = ctk.CTkTextbox(result_frame, height=100)
        self.mirror_result.pack(pady=5, fill="both", expand=True)

    def process_mirror(self):
        """Process text with mirror function"""
        text = self.mirror_input.get("1.0", "end-1c").strip()
        if text:
            result = mirror(text)
            self.mirror_result.delete("1.0", "end")
            self.mirror_result.insert("1.0", result)

    def open_cracking_interface(self):
        """Open the cracking interface"""
        self.cracking_btn.config(state='disabled')
        
        # Launch main without creating a new window
        # The main function should directly show password cracker and login
        main()
        
        # Re-enable the button after main closes
        self.enable_cracking_button()

    def open_steganography_interface(self):
        """Open the LSB Steganography Tool interface"""
        self.stego_btn.config(state='disabled')
        
        # Create and initialize SteganoApp
        stego_app = SteganoApp()
        
        def on_stego_close():
            self.enable_stego_button()
            stego_app.window.destroy()
        
        # Configure close protocol
        stego_app.window.protocol("WM_DELETE_WINDOW", on_stego_close)
        stego_app.window.mainloop()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CryptoInterface()
    app.run()
