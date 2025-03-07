import customtkinter as ctk

def caesar_cipher(clear, key):
    """Encrypt text using Caesar cipher."""
    if not isinstance(key, int):
        raise TypeError("Key must be an integer")
        
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(charset[(charset.index(c) + key) % len(charset)] if c in charset else c for c in clear)

def decrypt(cipher, key):
    """Decrypt text using Caesar cipher."""
    if not isinstance(key, int):
        raise TypeError("Key must be an integer")
        
    charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(charset[(charset.index(c) - key) % len(charset)] if c in charset else c for c in cipher)

class NumericSpinner(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.value = 1
        self.configure(fg_color="transparent")
        
        # Create spinner components
        self.entry = ctk.CTkEntry(self, width=60, justify="center")
        self.entry.insert(0, "1")
        self.entry.pack(side="left", padx=2)
        
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(side="left")
        
        # Up/Down buttons
        ctk.CTkButton(button_frame, text="▲", width=20, command=self.increment).pack()
        ctk.CTkButton(button_frame, text="▼", width=20, command=self.decrement).pack()
        
        # Validate entry
        self.entry.bind('<KeyRelease>', self.validate_input)
        
    def increment(self):
        self.value = min(99, self.value + 1)
        self.entry.delete(0, "end")
        self.entry.insert(0, str(self.value))
        
    def decrement(self):
        self.value = max(1, self.value - 1)
        self.entry.delete(0, "end")
        self.entry.insert(0, str(self.value))
        
    def validate_input(self, _):  # underscore indicates unused parameter
        try:
            value = self.entry.get()
            if value and value.isdigit():
                self.value = max(1, min(99, int(value)))
            else:
                self.value = 1
            self.entry.delete(0, "end")
            self.entry.insert(0, str(self.value))
        except ValueError:
            self.value = 1
            self.entry.delete(0, "end")
            self.entry.insert(0, "1")
            
    def get(self):
        return self.value

class CaesarCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Caesar Cipher")
        self.root.geometry("900x600")
        self.setup_gui()

    def setup_gui(self):
        # Create main container frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Key control frame at the top
        key_frame = ctk.CTkFrame(main_frame)
        key_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(key_frame, text="Encryption/Decryption Key:", font=("Arial", 12)).pack(side="left", padx=5)
        self.key_spinner = NumericSpinner(key_frame)
        self.key_spinner.pack(side="left", padx=5)

        # Encryption Frame (Left side)
        encrypt_frame = ctk.CTkFrame(main_frame)
        encrypt_frame.pack(side="left", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(encrypt_frame, text="Encryption", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Input frame for encryption
        enc_input_frame = ctk.CTkFrame(encrypt_frame)
        enc_input_frame.pack(pady=10, padx=20, fill="x")
        
        self.encrypt_entry = ctk.CTkTextbox(enc_input_frame, height=100)
        self.encrypt_entry.pack(pady=5, fill="x")
        
        ctk.CTkButton(enc_input_frame, text="Encrypt", command=self.encrypt_text).pack(pady=10)
        
        # Result frame for encryption
        enc_result_frame = ctk.CTkFrame(encrypt_frame)
        enc_result_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(enc_result_frame, text="Result:").pack(pady=5)
        self.encrypt_result = ctk.CTkTextbox(enc_result_frame, height=100)
        self.encrypt_result.pack(pady=5, fill="both", expand=True)

        # Decryption Frame (Right side)
        decrypt_frame = ctk.CTkFrame(main_frame)
        decrypt_frame.pack(side="right", expand=True, fill="both", padx=5)
        
        ctk.CTkLabel(decrypt_frame, text="Decryption", font=("Arial", 16, "bold")).pack(pady=5)
        
        # Input frame for decryption
        dec_input_frame = ctk.CTkFrame(decrypt_frame)
        dec_input_frame.pack(pady=10, padx=20, fill="x")
        
        self.decrypt_entry = ctk.CTkTextbox(dec_input_frame, height=100)
        self.decrypt_entry.pack(pady=5, fill="x")
        
        ctk.CTkButton(dec_input_frame, text="Decrypt", command=self.decrypt_text).pack(pady=10)
        
        # Result frame for decryption
        dec_result_frame = ctk.CTkFrame(decrypt_frame)
        dec_result_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(dec_result_frame, text="Result:").pack(pady=5)
        self.decrypt_result = ctk.CTkTextbox(dec_result_frame, height=100)
        self.decrypt_result.pack(pady=5, fill="both", expand=True)

    def encrypt_text(self):
        try:
            text = self.encrypt_entry.get("1.0", "end-1c").strip()
            if not text:
                raise ValueError("Please enter some text")
                
            key = self.key_spinner.get()
            result = caesar_cipher(text, key)
            
            self.encrypt_result.delete("1.0", "end")
            self.encrypt_result.insert("1.0", result)
        except ValueError as e:
            ctk.messagebox.showerror("Error", str(e))
        except Exception as e:
            ctk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def decrypt_text(self):
        try:
            text = self.decrypt_entry.get("1.0", "end-1c").strip()
            if not text:
                raise ValueError("Please enter some text")
                
            key = self.key_spinner.get()  # Using the same key spinner
            result = decrypt(text, key)
            
            self.decrypt_result.delete("1.0", "end")
            self.decrypt_result.insert("1.0", result)
        except ValueError as e:
            ctk.messagebox.showerror("Error", str(e))
        except Exception as e:
            ctk.messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = CaesarCipherApp(root)
    root.mainloop()
