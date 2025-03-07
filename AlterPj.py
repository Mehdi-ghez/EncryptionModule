import tkinter as tk
from Modules.login_window import LoginWindow
from Modules.cracker_window import CrackerWindow

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Create application state manager to handle communication
    app_state = {
        'is_login_locked': False,
        'lock_duration': 30,
        'max_attempts': 3,
        'count_per_password': True  # Flag to count each password guess as an attempt
    }
    
    # Create windows
    login_window = LoginWindow(root, app_state)
    cracker_window = CrackerWindow(root, app_state)
    
    # Set window references for communication
    login_window.set_cracker_window(cracker_window)
    cracker_window.set_login_window(login_window)
    
    # Position windows
    login_window.window.geometry("+100+200")
    cracker_window.window.geometry("+600+200")
    
    # Setup close handlers
    def on_closing():
        print("Closing application")
        if root:
            root.quit()
            root.destroy()
    
    login_window.window.protocol("WM_DELETE_WINDOW", on_closing)
    cracker_window.window.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
