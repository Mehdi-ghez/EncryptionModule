import customtkinter as ctk
from tkinter import messagebox

class AffineCipherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Affine Cipher")
        self.root.geometry("1200x600")  # Wider window for split view
        
        # Keys for affine cipher
        self.charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self.mod_size = len(self.charset)
        
        self.setup_gui()

    def setup_gui(self):
        # Main container with two frames
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(expand=True, fill="both", padx=10, pady=10)

        # Left frame (Encryption)
        self.encrypt_frame = ctk.CTkFrame(self.main_container)
        self.encrypt_frame.pack(side="left", expand=True, fill="both", padx=10)
        
        # Splitter (vertical line)
        self.splitter = ctk.CTkFrame(self.main_container, width=2, bg_color="gray50")
        self.splitter.pack(side="left", fill="y", padx=10)
        
        # Right frame (Decryption)
        self.decrypt_frame = ctk.CTkFrame(self.main_container)
        self.decrypt_frame.pack(side="right", expand=True, fill="both", padx=10)

        # Encryption Section
        self.setup_encryption_section()
        
        # Decryption Section
        self.setup_decryption_section()

    def setup_encryption_section(self):
        # Title
        self.encrypt_title = ctk.CTkLabel(self.encrypt_frame, text="Encryption", font=("Arial", 20, "bold"))
        self.encrypt_title.pack(pady=20)
        
        # Input
        self.encrypt_label = ctk.CTkLabel(self.encrypt_frame, text="Text to Encrypt:")
        self.encrypt_label.pack(pady=5)
        
        self.encrypt_input = ctk.CTkEntry(self.encrypt_frame, width=400)
        self.encrypt_input.pack(pady=5)
        
        # Key inputs
        self.key_frame = ctk.CTkFrame(self.encrypt_frame)
        self.key_frame.pack(pady=20)
        
        self.a_label = ctk.CTkLabel(self.key_frame, text="Key a:")
        self.a_label.pack(side="left", padx=5)
        
        self.a_entry = ctk.CTkEntry(self.key_frame, width=50)
        self.a_entry.pack(side="left", padx=5)
        self.a_entry.insert(0, "1")
        
        self.b_label = ctk.CTkLabel(self.key_frame, text="Key b:")
        self.b_label.pack(side="left", padx=5)
        
        self.b_entry = ctk.CTkEntry(self.key_frame, width=50)
        self.b_entry.pack(side="left", padx=5)
        self.b_entry.insert(0, "0")
        
        # Encrypt button
        self.encrypt_button = ctk.CTkButton(self.encrypt_frame, text="Encrypt", command=self.encrypt)
        self.encrypt_button.pack(pady=20)
        
        # Output
        self.encrypt_result_label = ctk.CTkLabel(self.encrypt_frame, text="Encrypted Result:")
        self.encrypt_result_label.pack(pady=5)
        
        self.encrypt_output = ctk.CTkTextbox(self.encrypt_frame, width=400, height=100)
        self.encrypt_output.pack(pady=5)

    def setup_decryption_section(self):
        # Title
        self.decrypt_title = ctk.CTkLabel(self.decrypt_frame, text="Decryption", font=("Arial", 20, "bold"))
        self.decrypt_title.pack(pady=20)
        
        # Input
        self.decrypt_label = ctk.CTkLabel(self.decrypt_frame, text="Text to Decrypt:")
        self.decrypt_label.pack(pady=5)
        
        self.decrypt_input = ctk.CTkEntry(self.decrypt_frame, width=400)
        self.decrypt_input.pack(pady=5)
        
        # Decrypt button
        self.decrypt_button = ctk.CTkButton(self.decrypt_frame, text="Decrypt", command=self.decrypt)
        self.decrypt_button.pack(pady=20)
        
        # Output
        self.decrypt_result_label = ctk.CTkLabel(self.decrypt_frame, text="Decrypted Result:")
        self.decrypt_result_label.pack(pady=5)
        
        self.decrypt_output = ctk.CTkTextbox(self.decrypt_frame, width=400, height=100)
        self.decrypt_output.pack(pady=5)

    def mod_inverse(self, a, m):
        for x in range(1, m):
            if (a * x) % m == 1:
                return x
        return 1

    def validate_keys(self):
        try:
            a = int(self.a_entry.get())
            b = int(self.b_entry.get())
            
            if a < 1 or b < 0 or b >= self.mod_size:
                messagebox.showerror("Error", f"Invalid keys: 'a' must be positive, 'b' must be between 0 and {self.mod_size-1}")
                return False
            
            # Check if 'a' is coprime with mod_size (62)
            if self.mod_inverse(a, self.mod_size) == 1 and a != 1:
                messagebox.showerror("Error", f"'a' must be coprime with {self.mod_size}")
                return False
                
            return True
        except ValueError:
            messagebox.showerror("Error", "Keys must be numbers")
            return False

    def number_to_char(self, number):
        """Convert a number to its corresponding character from the charset"""
        if 0 <= number < self.mod_size:
            return self.charset[number]
        return self.charset[0]  # default return

    def char_to_number(self, char):
        """Convert a character to its corresponding number from the charset"""
        if char in self.charset:
            return self.charset.index(char)
        return 0  # default return

    def is_valid_a(self, a):
        """Check if a number is valid for key 'a' (must be coprime with mod_size)"""
        if a < 1:
            return False
        return self.mod_inverse(a, self.mod_size) != 1 or a == 1

    def get_keys_from_word(self, word):
        """Extract potential keys from a word"""
        if len(word) < 2:
            return None, None
        
        # Try to find valid 'a' key from consecutive characters
        a = None
        b = None
        
        # Try each pair of consecutive characters
        for i in range(len(word) - 1):
            if word[i] in self.charset and word[i+1] in self.charset:
                potential_a = self.char_to_number(word[i])
                potential_b = self.char_to_number(word[i+1])
                
                if self.is_valid_a(potential_a):
                    a = potential_a
                    b = potential_b
                    break
        
        return a, b

    def encrypt_word(self, word, a, b):
        """Encrypt a single word using affine cipher"""
        result = ""
        for char in word:
            if char in self.charset:
                x = self.charset.index(char)
                encrypted_num = (a * x + b) % self.mod_size
                result += self.charset[encrypted_num]
            else:
                result += char
        return result

    def get_keys_from_plaintext(self, text):
        """Get valid keys from first two characters of plaintext"""
        if len(text) < 2:
            return None, None
            
        # Get positions of first two characters
        try:
            a = self.charset.index(text[0])
            b = self.charset.index(text[1])
            
            # Validate 'a' is suitable (coprime with charset length)
            if self.is_valid_a(a):
                return a, b
        except:
            pass
        return None, None

    def encrypt(self):
        if not self.validate_keys():
            return
            
        text = self.encrypt_input.get()
        words = text.split()
        if not words:
            return
        
        # Initialize with user-provided keys
        current_a = int(self.a_entry.get())
        current_b = int(self.b_entry.get())
        
        encrypted_words = []
        
        # Encrypt first word with initial keys and add markers
        first_encrypted = self.encrypt_word(words[0], current_a, current_b)
        a_char = self.number_to_char(current_a)
        b_char = self.number_to_char(current_b)
        encrypted_words.append(f"{a_char}{first_encrypted}{b_char}")
        
        # Process remaining words
        for i in range(1, len(words)):
            # Try to get new keys from previous plaintext word
            new_a, new_b = self.get_keys_from_plaintext(words[i-1])
            
            if new_a is not None and new_b is not None:
                current_a = new_a
                current_b = new_b
            
            # Encrypt word without markers
            encrypted_word = self.encrypt_word(words[i], current_a, current_b)
            encrypted_words.append(encrypted_word)
        
        final_result = " ".join(encrypted_words)
        self.encrypt_output.delete("0.0", "end")
        self.encrypt_output.insert("0.0", final_result)

    def decrypt(self):
        text = self.decrypt_input.get()
        words = text.split()
        if not words:
            return
        
        decrypted_words = []
        
        # Handle first word - extract keys from markers
        first_word = words[0]
        if len(first_word) < 3:
            return
            
        # Get initial keys from markers
        current_a = self.char_to_number(first_word[0])
        current_b = self.char_to_number(first_word[-1])
        main_text = first_word[1:-1]
        
        # Decrypt first word
        a_inv = self.mod_inverse(current_a, self.mod_size)
        first_result = ""
        for char in main_text:
            if char in self.charset:
                x = self.charset.index(char)
                decrypted_num = (a_inv * (x - current_b)) % self.mod_size
                first_result += self.charset[decrypted_num]
            else:
                first_result += char
        decrypted_words.append(first_result)
        
        # Process remaining words
        for i in range(1, len(words)):
            # Get keys from previous decrypted word
            new_a, new_b = self.get_keys_from_plaintext(decrypted_words[-1])
            
            if new_a is not None and new_b is not None:
                current_a = new_a
                current_b = new_b
            
            # Decrypt current word
            encrypted_word = words[i]
            a_inv = self.mod_inverse(current_a, self.mod_size)
            
            result = ""
            for char in encrypted_word:
                if char in self.charset:
                    x = self.charset.index(char)
                    decrypted_num = (a_inv * (x - current_b)) % self.mod_size
                    result += self.charset[decrypted_num]
                else:
                    result += char
            
            decrypted_words.append(result)
        
        final_result = " ".join(decrypted_words)
        self.decrypt_output.delete("0.0", "end")
        self.decrypt_output.insert("0.0", final_result)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = AffineCipherApp(root)
    root.mainloop()
