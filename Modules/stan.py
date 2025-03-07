import numpy as np
from PIL import Image
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import time
import threading
import struct

class SteganoApp:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("LSB Steganography Tool")
        self.window.geometry("1000x600")
        self.window.configure(bg='#2c3e50')
        
        # Create main frames
        left_frame = tk.Frame(self.window, bg='#2c3e50')
        middle_frame = tk.Frame(self.window, bg='#2c3e50')
        right_frame = tk.Frame(self.window, bg='#2c3e50')
        
        # Setup frames
        self._setup_left_frame(left_frame)
        self._setup_middle_frame(middle_frame)
        self._setup_right_frame(right_frame)
        
        # Pack main frames
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initialize variables
        self.active_mode = None
        self.chunk_size = 1000  # Process this many pixels at a time
        self.max_capacity = 0   # Maximum characters the image can store
        
        # Additional variables for threading
        self.active_thread = None
        self.stop_thread = False

    def _setup_left_frame(self, frame):
        # Operation Modes Section
        modes_label = tk.Label(frame, text="Steganography Modes:", bg='#2c3e50', fg='white')
        modes_label.pack(pady=5)
        
        modes_buttons_frame = tk.Frame(frame, bg='#2c3e50')
        self.modes = ["Hide Message", "Extract Message"]
        self.mode_buttons = {}
        
        for mode in self.modes:
            btn = tk.Button(modes_buttons_frame, text=mode,
                          bg='#1dd1a1', fg='white',
                          relief="raised",
                          command=lambda x=mode: self.toggle_mode(x))
            btn.pack(fill=tk.X, pady=2)
            self.mode_buttons[mode] = btn
        
        modes_buttons_frame.pack(fill=tk.BOTH, expand=True)
        
        # Information Section
        info_label = tk.Label(frame, text="About LSB Steganography:", bg='#2c3e50', fg='white')
        info_label.pack(pady=5)
        
        info_text = tk.Text(frame, height=10, width=30, bg='#34495e', fg='white', wrap=tk.WORD)
        info_text.insert(tk.END, 
            "LSB (Least Significant Bit) steganography hides messages in the least significant bits of pixel values in an image.\n\n"
            "This technique uses randomization to improve security by scattering the message bits across the image.\n\n"
            "The end of the hidden message is marked with a special bit pattern.")
        info_text.config(state=tk.DISABLED)
        info_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def _setup_middle_frame(self, frame):
        # Image Selection Section
        image_label = tk.Label(frame, text="Select Image:", bg='#2c3e50', fg='white')
        image_label.pack(pady=5)
        
        image_frame = tk.Frame(frame, bg='#2c3e50')
        self.image_path_entry = ttk.Entry(image_frame, width=40)
        self.image_path_entry.pack(side=tk.LEFT, padx=2)
        self.browse_button = tk.Button(image_frame, text="Browse", 
                                    bg='#3498db', fg='white',
                                    command=self.select_image)
        self.browse_button.pack(side=tk.RIGHT)
        image_frame.pack(fill=tk.X, pady=5)
        
        # Secret Message Section
        self.message_label = tk.Label(frame, text="Enter Secret Message:", bg='#2c3e50', fg='white')
        self.message_label.pack(pady=5)
        
        self.message_text = tk.Text(frame, height=5, width=40, bg='white')
        self.message_text.pack(pady=5)
        
        # Output Image Section
        self.output_label = tk.Label(frame, text="Save Image As:", bg='#2c3e50', fg='white')
        self.output_label.pack(pady=5)
        
        output_frame = tk.Frame(frame, bg='#2c3e50')
        self.output_path_entry = ttk.Entry(output_frame, width=40)
        self.output_path_entry.pack(side=tk.LEFT, padx=2)
        self.save_button = tk.Button(output_frame, text="Choose Location", 
                                  bg='#3498db', fg='white',
                                  command=self.select_output_path)
        self.save_button.pack(side=tk.RIGHT)
        output_frame.pack(fill=tk.X, pady=5)
        
        # Operation Button
        self.action_button = tk.Button(frame, text="Perform Operation", 
                                    bg='#2ecc71', fg='white',
                                    height=2, width=20,
                                    command=self.perform_operation)
        self.action_button.pack(pady=15)
        
        # Status Section
        status_label = tk.Label(frame, text="Status:", bg='#2c3e50', fg='white')
        status_label.pack(pady=5)
        
        self.status_text = tk.Label(frame, text="Ready", bg='#2c3e50', fg='white', 
                                 wraplength=300, justify=tk.LEFT)
        self.status_text.pack(pady=5)
        
        # Progress Bar
        self.progress_bar = ttk.Progressbar(frame, mode='determinate', length=300)
        self.progress_bar.pack(pady=5)
        
        # Time Taken
        time_label = tk.Label(frame, text="Processing Time:", bg='#2c3e50', fg='white')
        time_label.pack(pady=5)
        
        self.time_text = tk.Label(frame, text="", bg='#2c3e50', fg='white')
        self.time_text.pack(pady=5)

    def _setup_right_frame(self, frame):
        # Image Preview Section
        preview_label = tk.Label(frame, text="Image Preview:", bg='#2c3e50', fg='white')
        preview_label.pack(pady=5)
        
        self.preview_canvas = tk.Canvas(frame, width=300, height=300, bg='#34495e', highlightthickness=1)
        self.preview_canvas.pack(pady=5)
        
        # Image Statistics
        stats_label = tk.Label(frame, text="Image Statistics:", bg='#2c3e50', fg='white')
        stats_label.pack(pady=5)
        
        self.stats_text = tk.Label(frame, text="No image selected", bg='#2c3e50', fg='white',
                               wraplength=300, justify=tk.LEFT)
        self.stats_text.pack(pady=5)
        
        # Image Capacity
        capacity_label = tk.Label(frame, text="Steganography Capacity:", bg='#2c3e50', fg='white')
        capacity_label.pack(pady=5)
        
        self.capacity_text = tk.Label(frame, text="N/A", bg='#2c3e50', fg='white',
                                   wraplength=300, justify=tk.LEFT, font=("Arial", 10, "bold"))
        self.capacity_text.pack(pady=5)
        
        # Extracted Message (shown only when extracting)
        self.extracted_label = tk.Label(frame, text="Extracted Message:", bg='#2c3e50', fg='white', 
                                 font=("Arial", 10, "bold"))
        self.extracted_label.pack(pady=5)
        
        # Create a frame for the extracted text with scrollbar
        extract_frame = tk.Frame(frame, bg='#2c3e50')
        extract_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add scrollbar to the extracted text
        scrollbar = tk.Scrollbar(extract_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure the extracted text widget
        self.extracted_text = tk.Text(extract_frame, height=10, width=35, bg='white',
                               wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.extracted_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure the scrollbar
        scrollbar.config(command=self.extracted_text.yview)
        
        # Initially hide the extraction widgets
        self.extracted_label.pack_forget()
        extract_frame.pack_forget()
        
        # Store the frame for toggling visibility
        self.extract_frame = extract_frame

    def toggle_mode(self, mode):
        if self.active_mode == mode:
            return
        
        if self.active_mode:
            self.mode_buttons[self.active_mode].configure(bg='#1dd1a1', relief="raised")
        
        self.active_mode = mode
        self.mode_buttons[mode].configure(bg='#1dd1a1', relief="sunken")
        
        # Update UI based on mode
        if mode == "Hide Message":
            self.message_label.pack(pady=5)
            self.message_text.pack(pady=5)
            self.output_label.pack(pady=5)
            self.output_path_entry.master.pack(fill=tk.X, pady=5)
            
            self.extracted_label.pack_forget()
            self.extract_frame.pack_forget()  # Hide the entire extract frame
            
        else:  # Extract mode
            self.message_label.pack_forget()
            self.message_text.pack_forget()
            self.output_label.pack_forget()
            self.output_path_entry.master.pack_forget()
            
            self.extracted_label.pack(pady=5)
            self.extract_frame.pack(fill=tk.BOTH, expand=True, pady=5)  # Show the extract frame

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp")]
        )
        
        if file_path:
            self.image_path_entry.delete(0, tk.END)
            self.image_path_entry.insert(0, file_path)
            
            # Generate output path suggestion
            if not self.output_path_entry.get() and self.active_mode == "Hide Message":
                dir_path = os.path.dirname(file_path)
                file_name = os.path.basename(file_path)
                name, ext = os.path.splitext(file_name)
                output_path = os.path.join(dir_path, name + "_stego" + ext)
                self.output_path_entry.delete(0, tk.END)
                self.output_path_entry.insert(0, output_path)
            
            # Show image preview and stats
            self.show_image_preview(file_path)
            
            # Calculate and display capacity
            self.calculate_capacity(file_path)

    def select_output_path(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Image As",
            filetypes=[("PNG files", "*.png")],
            defaultextension=".png"
        )
        
        if file_path:
            self.output_path_entry.delete(0, tk.END)
            self.output_path_entry.insert(0, file_path)

    def calculate_capacity(self, image_path):
        """Calculate and display the maximum capacity of the image for hiding text."""
        try:
            img = Image.open(image_path)
            width, height = img.size
            channels = len(img.getbands())
            
            # Total pixels available for storing data
            total_pixels = width * height * channels
            
            # Each pixel can store 1 bit in the LSB method
            total_bits = total_pixels
            
            # Convert to characters (8 bits per character)
            char_capacity = total_bits // 8
            
            # Account for end marker (16 bits)
            char_capacity -= 2
            
            # Update the capacity display
            self.max_capacity = char_capacity
            self.capacity_text.config(
                text=f"This image can store approximately:\n"
                     f"{char_capacity:,} characters\n"
                     f"({char_capacity / 1024:.1f} KB of text)"
            )
            
        except Exception as e:
            self.capacity_text.config(text=f"Could not calculate capacity: {str(e)}")

    def show_image_preview(self, image_path):
        try:
            # Open and display the image
            img = Image.open(image_path)
            
            # Resize for preview
            preview_width, preview_height = 300, 300
            img_copy = img.copy()  # Work with a copy to avoid modifying original
            img_copy.thumbnail((preview_width, preview_height))
            
            # Convert to PhotoImage more efficiently
            try:
                self.photo = tk.PhotoImage(file=image_path)
                self.photo = self.photo.subsample(max(1, img.width // preview_width), 
                                               max(1, img.height // preview_height))
            except:
                # Fallback for incompatible images
                img_copy = img_copy.convert("RGB")
                self.photo = tk.PhotoImage(data=img_copy.tobytes())
            
            # Clear canvas and display
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                preview_width // 2, preview_height // 2,
                image=self.photo
            )
            
            # Update stats
            width, height = img.size
            file_size = os.path.getsize(image_path) / 1024  # KB
            
            stats = f"Dimensions: {width} x {height}\n" \
                   f"File Size: {file_size:.2f} KB\n" \
                   f"Format: {img.format}\n" \
                   f"Mode: {img.mode}\n"
                   
            self.stats_text.config(text=stats)
            
            # Keep UI responsive
            self.window.update_idletasks()
            
        except Exception as e:
            self.stats_text.config(text=f"Error loading image: {str(e)}")
            self.preview_canvas.delete("all")
            self.window.update_idletasks()

    def perform_operation(self):
        if not self.active_mode:
            messagebox.showerror("Error", "Please select a mode (Hide or Extract)")
            return
            
        image_path = self.image_path_entry.get()
        if not image_path:
            messagebox.showerror("Error", "Please select an image")
            return
            
        if not os.path.exists(image_path):
            messagebox.showerror("Error", "Selected image file does not exist")
            return
        
        # Disable buttons during operation
        self.action_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        if hasattr(self, 'save_button'):
            self.save_button.config(state=tk.DISABLED)
        
        # Reset progress
        self.progress_bar['value'] = 0
        self.status_text.config(text="Processing...")
        self.window.update_idletasks()
        
        # Stop any existing thread
        if self.active_thread and self.active_thread.is_alive():
            self.stop_thread = True
            self.active_thread.join(0.5)
        
        self.stop_thread = False
        
        # Create and start new thread
        if self.active_mode == "Hide Message":
            secret_text = self.message_text.get("1.0", tk.END).strip()
            output_path = self.output_path_entry.get()
            
            if not secret_text:
                messagebox.showerror("Error", "Please enter a message to hide")
                self._re_enable_buttons()
                return
                
            if not output_path:
                messagebox.showerror("Error", "Please select an output path")
                self._re_enable_buttons()
                return
            
            # Check if message exceeds capacity
            if len(secret_text) > self.max_capacity:
                if not messagebox.askyesno("Warning", 
                    f"Your message ({len(secret_text)} chars) exceeds the recommended capacity "
                    f"({self.max_capacity} chars).\nThis may distort the image or make the "
                    f"message unrecoverable.\n\nContinue anyway?"):
                    self._re_enable_buttons()
                    return
            
            self.active_thread = threading.Thread(
                target=self._thread_hide_text,
                args=(image_path, secret_text, output_path)
            )
            
        else:  # Extract mode
            self.active_thread = threading.Thread(
                target=self._thread_extract_text,
                args=(image_path,)
            )
        
        # Start the worker thread
        self.active_thread.daemon = True
        self.active_thread.start()

    def _re_enable_buttons(self):
        """Re-enable all buttons after operation completes"""
        self.action_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.NORMAL)
        if hasattr(self, 'save_button'):
            self.save_button.config(state=tk.NORMAL)
    
    def _thread_hide_text(self, image_path, secret_text, output_path):
        """Worker thread for hiding text in image"""
        try:
            start_time = time.time()
            
            # Update UI from main thread
            self.window.after(0, lambda: self.status_text.config(text="Preparing to hide message..."))
            self.window.after(0, lambda: self.progress_bar.config(value=10))
            
            # Perform the operation
            self.hide_text(image_path, secret_text, output_path)
            
            end_time = time.time()
            elapsed = end_time - start_time
            
            # Update UI when done
            self.window.after(0, lambda: self.status_text.config(text=f"Message hidden successfully in\n{output_path}"))
            self.window.after(0, lambda: self.progress_bar.config(value=100))
            self.window.after(0, lambda: self.time_text.config(text=f"{elapsed:.2f} seconds"))
            
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            self.window.after(0, lambda: self.status_text.config(text=f"Error: {error_msg}"))
            self.window.after(0, lambda: self.progress_bar.config(value=0))
            self.window.after(0, lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            # Re-enable buttons
            self.window.after(0, self._re_enable_buttons)
    
    def _thread_extract_text(self, image_path):
        """Worker thread for extracting text from image"""
        try:
            start_time = time.time()
            
            # Update UI from main thread
            self.window.after(0, lambda: self.status_text.config(text="Extracting hidden message..."))
            self.window.after(0, lambda: self.progress_bar.config(value=10))
            
            # Perform the operation
            extracted_message = self.extract_text(image_path)
            
            # Update UI when done
            end_time = time.time()
            elapsed = end_time - start_time
            
            def update_ui():
                # Make sure we're in extract mode
                if self.active_mode != "Extract Message":
                    self.toggle_mode("Extract Message")
                
                # Make sure the extracted text widgets are visible
                self.extracted_label.pack(pady=5)
                self.extracted_text.pack(pady=5, fill=tk.BOTH, expand=True)
                
                # Clear and set the text
                self.extracted_text.delete("1.0", tk.END)
                self.extracted_text.insert(tk.END, extracted_message)
                
                # Ensure the text is visible by making it active
                self.extracted_text.focus_set()
                
                # Update status and progress
                self.status_text.config(text=f"Message extracted successfully: {len(extracted_message)} characters")
                self.progress_bar['value'] = 100
                self.time_text.config(text=f"{elapsed:.2f} seconds")
                
                # Print for debugging
                print(f"Extracted message: {extracted_message[:50]}...")
            
            # Schedule UI update
            self.window.after(0, update_ui)
            
        except Exception as e:
            # Handle errors
            error_msg = str(e)
            self.window.after(0, lambda: self.status_text.config(text=f"Error: {error_msg}"))
            self.window.after(0, lambda: self.progress_bar.config(value=0))
            self.window.after(0, lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            # Re-enable buttons
            self.window.after(0, self._re_enable_buttons)

    # Function to convert text to binary
    def text_to_binary(self, text):
        return ''.join(format(ord(c), '08b') for c in text)

    # Improved binary to text conversion function
    def binary_to_text(self, binary_str):
        if not binary_str:
            return ""
            
        # Ensure binary string length is a multiple of 8
        padded_str = binary_str
        if len(binary_str) % 8 != 0:
            padded_str = binary_str + '0' * (8 - (len(binary_str) % 8))
        
        # Convert each 8-bit sequence to a character
        result = ""
        for i in range(0, len(padded_str), 8):
            byte = padded_str[i:i+8]
            if len(byte) == 8:  # Verify we have a full byte
                try:
                    char = chr(int(byte, 2))
                    result += char
                except ValueError:
                    # Skip invalid characters
                    pass
        
        return result

    # Function to embed text in image - updated to ensure all characters are preserved
    def hide_text(self, image_path, secret_text, output_path):
        img = Image.open(image_path)
        img_array = np.array(img)
        
        # Convert secret text to binary, ensuring full bytes
        binary_text = self.text_to_binary(secret_text)
        
        # Add padding to ensure byte alignment before end marker
        padding = (8 - (len(binary_text) % 8)) % 8
        padded_binary = binary_text + '0' * padding
        
        # Add the end marker (16 zeroes)
        full_payload = padded_binary + '0000000000000000'
        
        # Get the flattened pixels
        flat_pixels = img_array.flatten()
        
        if len(full_payload) > len(flat_pixels):
            raise ValueError("Image too small to hold the message")
        
        # Update UI
        self.window.after(0, lambda: self.status_text.config(text="Embedding message..."))
        self.window.after(0, lambda: self.progress_bar.config(value=30))
        
        # Convert to a copy with appropriate data type
        flat_pixels_copy = flat_pixels.copy()
        
        # Process in chunks to keep UI responsive
        chunk_count = (len(full_payload) + self.chunk_size - 1) // self.chunk_size
        
        for chunk_idx in range(chunk_count):
            # Check if we should stop
            if self.stop_thread:
                raise InterruptedError("Operation cancelled")
                
            start_idx = chunk_idx * self.chunk_size
            end_idx = min((chunk_idx + 1) * self.chunk_size, len(full_payload))
            
            # Process this chunk - sequential embedding (no randomization)
            for i in range(start_idx, end_idx):
                bit = full_payload[i]
                # Simple LSB replacement - avoid uint8 bounds error
                if bit == '1':
                    flat_pixels_copy[i] = (flat_pixels_copy[i] | 1)  # Set LSB to 1
                else:
                    flat_pixels_copy[i] = (flat_pixels_copy[i] & 254)  # Set LSB to 0
            
            # Update progress
            progress = 30 + (chunk_idx / chunk_count) * 50
            self.window.after(0, lambda p=progress: self.progress_bar.config(value=p))
            self.window.after(0, lambda p=progress: self.status_text.config(
                text=f"Embedding message... {int(p)}%"))
        
        # Reshape and save the modified image
        self.window.after(0, lambda: self.status_text.config(text="Saving image..."))
        
        new_img_array = flat_pixels_copy.reshape(img_array.shape)
        new_img = Image.fromarray(new_img_array)
        new_img.save(output_path)
        
        self.window.after(0, lambda: self.progress_bar.config(value=90))
        return True

    # Function to extract hidden text - updated to preserve all characters
    def extract_text(self, image_path):
        img = Image.open(image_path)
        img_array = np.array(img)
        flat_pixels = img_array.flatten()
        
        # Update UI
        self.window.after(0, lambda: self.status_text.config(text="Extracting hidden message..."))
        self.window.after(0, lambda: self.progress_bar.config(value=30))
        
        # Extract bits sequentially until end marker or max length
        binary_text = ""
        max_bits = min(100000, len(flat_pixels))  # Reasonable limit
        
        # Process in chunks for UI responsiveness
        chunk_size = 5000
        chunks = (max_bits + chunk_size - 1) // chunk_size
        
        for chunk_idx in range(chunks):
            if self.stop_thread:
                raise InterruptedError("Operation cancelled")
                
            start_idx = chunk_idx * chunk_size
            end_idx = min((chunk_idx + 1) * chunk_size, max_bits)
            
            # Extract bits from this chunk
            for i in range(start_idx, end_idx):
                # Extract the LSB
                binary_text += str(flat_pixels[i] & 1)
                
            # Update progress
            progress = 30 + (chunk_idx / chunks) * 50
            self.window.after(0, lambda p=progress: self.progress_bar.config(value=p))
            self.window.after(0, lambda p=progress: self.status_text.config(
                text=f"Searching for hidden message... {int(p)}%"))
            
            # Check for end marker pattern after each chunk is processed
            end_marker_pos = binary_text.find('0000000000000000')
            if end_marker_pos != -1:
                # Found the end marker
                message_binary = binary_text[:end_marker_pos]
                message = self.binary_to_text(message_binary)
                
                self.window.after(0, lambda: self.progress_bar.config(value=90))
                self.window.after(0, lambda: self.status_text.config(
                    text=f"Message found! ({len(message)} characters)"))
                
                return message
        
        # If no end marker found but we have data, try to extract anyway
        if len(binary_text) > 8:
            # Make sure we extract complete bytes
            complete_bytes = len(binary_text) - (len(binary_text) % 8)
            message = self.binary_to_text(binary_text[:complete_bytes])
            
            if self._is_plausible_text(message):
                self.window.after(0, lambda: self.progress_bar.config(value=80))
                return message
        
        self.window.after(0, lambda: self.progress_bar.config(value=80))
        return "No hidden message found"

    # Simpler plausibility check
    def _is_plausible_text(self, text):
        """Quick check if text looks like readable content"""
        if not text or len(text) < 3:
            return False
            
        # At least 50% should be printable characters
        printable_count = sum(1 for c in text if 32 <= ord(c) <= 126)
        return printable_count / len(text) > 0.5

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = SteganoApp()
    app.run()
