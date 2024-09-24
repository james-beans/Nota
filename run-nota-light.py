from datetime import datetime
import webbrowser
import re
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, font

class WordNotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Nota Light - No clutter notes.")

        # Instance variable for file types
        self.filetypes = [
            ("Text files", "*.txt"),
            ("All files", "*.*")
        ]

        # Last command initialization
        self.last_command = ""
        self.file_path = None
        self.is_dark_mode = False  # Track the dark mode state

        # Font settings
        self.default_font_size = 12
        self.current_font_size = self.default_font_size
        self.max_zoom_in_size = self.default_font_size + 13  # Maximum font size after zooming in

        # Top Menu bar.

        # Create a menu bar at the top
        self.menu_bar = tk.Menu(root)
        root.config(menu=self.menu_bar)

        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="New File", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open File", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save As", accelerator="Ctrl+A", command=self.save_as)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.redo)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        view_menu.add_command(label="New Window", accelerator="Ctrl+Shift+N", command=self.new_window)
        view_menu.add_command(label="Switch to light/dark mode", accelerator="Ctrl+D", command=self.toggle_dark_mode)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        # Info menu
        Info_menu = tk.Menu(self.menu_bar, tearoff=0)
        Info_menu.add_command(label="Upgrade to Nota (full)", accelerator="Ctrl+U", command=self.upgrade)
        Info_menu.add_command(label="Docs", accelerator="Ctrl+Alt+D", command=self.docs)
        Info_menu.add_command(label="Issues", accelerator="Ctrl+Alt+F", command=self.issues)
        Info_menu.add_command(label="Github", accelerator="Ctrl+Alt+G", command=self.gitlnk)
        Info_menu.add_command(label="Credits", accelerator="Ctrl+Alt+P", command=self.credits)
        self.menu_bar.add_cascade(label="Info", menu=Info_menu)

        # Text widget properties

        # Create a frame for the text widget with a fixed height
        self.text_frame = tk.Frame(root)
        self.text_frame.pack(expand=True, fill='both')

        # Text widget for notes with undo/redo enabled
        self.text_widget = tk.Text(self.text_frame, wrap=tk.WORD, undo=True, font=("Helvetica", self.current_font_size))
        self.text_widget.pack(expand=True, fill='both', padx=5, pady=5)

        # Disable the text widget initially
        self.text_widget.config(state=tk.DISABLED)

        # Bottom/Status Bar

        # Create a frame to hold the status bar and dark mode toggle, placed at the bottom
        self.bottom_frame = tk.Frame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Add a status label to the bottom-left for displaying messages
        self.status_label = tk.Label(self.bottom_frame, text="Welcome to Nota!", anchor="w")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5, fill=tk.X)

        # Add dark mode toggle button to the bottom-right
        self.toggle_button = tk.Button(self.bottom_frame, text="🌞", command=self.toggle_dark_mode)
        self.toggle_button.pack(side=tk.RIGHT, padx=10, pady=5)

        # Add Zoom In and Zoom Out buttons
        self.zoom_in_button = tk.Button(self.bottom_frame, text="Zoom In", command=self.zoom_in)
        self.zoom_in_button.pack(side=tk.RIGHT, padx=5, pady=5)

        self.zoom_out_button = tk.Button(self.bottom_frame, text="Zoom Out", command=self.zoom_out)
        self.zoom_out_button.pack(side=tk.RIGHT, padx=5, pady=5)

        # MISC properties

        # Bind key shortcuts
        root.bind("<Control-n>", lambda event: self.new_file())
        root.bind("<Control-o>", lambda event: self.open_file())
        root.bind("<Control-s>", lambda event: self.save_file())
        root.bind("<Control-a>", lambda event: self.save_as())
        root.bind("<Control-z>", lambda event: self.undo())
        root.bind("<Control-y>", lambda event: self.redo())
        root.bind("<Control-N>", lambda event: self.new_window())
        root.bind("<Control-d>", lambda event: self.toggle_dark_mode())
        root.bind("<Control-Alt-p>", lambda event: self.credits())
        root.bind("<Control-Alt-g>", lambda event: self.gitlnk())
        root.bind("<Control-u>", lambda event: self.upgrade())
        root.bind("<Control-Alt-d>", lambda event: self.docs())
        root.bind("<Control-Alt-f>", lambda event: self.issues())

        # Status Bar tooltip call events
        # Bind hover events for tooltips
        self.text_widget.bind("<Enter>", lambda e: self.update_status("Edit text here."))
        self.text_widget.bind("<Leave>", lambda e: self.clear_status())
        self.toggle_button.bind("<Enter>", lambda e: self.update_status("Toggle between light/dark mode."))
        self.toggle_button.bind("<Leave>", lambda e: self.clear_status())
        self.zoom_in_button.bind("<Enter>", lambda e: self.update_status("Zoom In."))
        self.zoom_in_button.bind("<Leave>", lambda e: self.clear_status())
        self.zoom_out_button.bind("<Enter>", lambda e: self.update_status("Zoom Out."))
        self.zoom_out_button.bind("<Leave>", lambda e: self.clear_status())

    # Functions to call in other code:
    # def = define functions.

    # Toggle dark mode
    def toggle_dark_mode(self):
        if self.is_dark_mode:
            # Switch to light mode
            self.root.config(bg="SystemButtonFace")
            self.text_widget.config(bg="white", fg="black", insertbackground="black")
            self.toggle_button.config(text="🌞")  # Sun emoji for light mode
            self.bottom_frame.config(bg="#f0f0f0")  # Light color for bottom frame
            self.update_status("Switched to light mode.")
        else:
            # Switch to dark mode
            self.root.config(bg="black")
            self.text_widget.config(bg="#1f1f1f", fg="white", insertbackground="white")
            self.toggle_button.config(text="🌙")  # Moon emoji for dark mode
            self.bottom_frame.config(bg="#181818")  # Dark color for bottom frame
            self.update_status("Switched to dark mode.")

        self.is_dark_mode = not self.is_dark_mode  # Toggle the dark mode state

    # Zoom in (increase the font size)
    def zoom_in(self):
        if self.current_font_size < self.max_zoom_in_size:  # Check for maximum zoom-in limit
            self.current_font_size += 1
            self.text_widget.config(font=("Helvetica", self.current_font_size))
            self.update_status("Zoomed in.")
        else:
            self.update_status("Maximum zoom in reached.")

    # Zoom out (decrease the font size)
    def zoom_out(self):
        if self.current_font_size > 1:  # Prevent zooming out too much
            self.current_font_size -= 1
            self.text_widget.config(font=("Helvetica", self.current_font_size))
            self.update_status("Zoomed out.")
        else:
            self.update_status("Cannot zoom out further.")

    # File menu actions
    def new_file(self):
        self.text_widget.config(state=tk.NORMAL)  # Enable text input
        self.text_widget.delete("1.0", tk.END)
        self.file_path = None
        self.text_widget.edit_reset()  # Reset undo/redo stack for the new file
        self.update_status("New file created.")

    def open_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=self.filetypes)
        if self.file_path:
            with open(self.file_path, "r") as file:
                content = file.read()
            self.text_widget.config(state=tk.NORMAL)  # Enable text input
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.insert("1.0", content)
            self.text_widget.edit_reset()  # Reset undo/redo stack after opening the file
            self.update_status(f"Opened file: {self.file_path}")

    def save_file(self):
        if self.file_path:
            with open(self.file_path, "w") as file:
                file.write(self.text_widget.get("1.0", tk.END))
            self.update_status(f"File saved: {self.file_path}")
        else:
            self.save_as()

    def save_as(self):
        self.file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=self.filetypes)
        if self.file_path:
            self.save_file()

    # Edit menu actions
    def undo(self):
        try:
            self.text_widget.edit_undo()
            self.update_status("Undo performed.")
        except tk.TclError:
            self.update_status("Nothing to undo.")

    def redo(self):
        try:
            self.text_widget.edit_redo()
            self.update_status("Redo performed.")
        except tk.TclError:
            self.update_status("Nothing to redo.")

    def new_window(self):
        new_root = tk.Toplevel(self.root)  # Create a new top-level window
        new_app = WordNotesApp(new_root)   # Create a new instance of the app for the new window
        self.update_status("New window opened.")

    # Status label management
    def update_status(self, message):
        self.status_label.config(text=message)

    def clear_status(self):
        self.status_label.config(text="")

    # Opens CREDITS.md in the Github repo
    def credits(self):
        try:
            webbrowser.open("https://github.com/james-beans/Nota/blob/main/CREDITS.md")
            self.update_status(f"Opened link in browser.")
        except Exception:
            self.update_status("401::Error::Link failed.")

    # Opens the Github repo for Nota
    def gitlnk(self):
        try:
            webbrowser.open("https://github.com/james-beans/Nota/")
            self.update_status(f"Opened link in browser.")
        except Exception:
            self.update_status("401::Error::Link failed.")

    # Opens UPGRADE.md in the Github repo
    def upgrade(self):
        try:
            webbrowser.open("https://github.com/james-beans/Nota/blob/main/UPGRADE.md")
            self.update_status(f"Opened link in browser.")
        except Exception:
            self.update_status("401::Error::Link failed.")

    # Opens UPGRADE.md in the Github repo
    def docs(self):
        try:
            webbrowser.open("https://github.com/james-beans/Nota/wiki")
            self.update_status(f"Opened link in browser.")
        except Exception:
            self.update_status("401::Error::Link failed.")
    
    # Opens UPGRADE.md in the Github repo
    def issues(self):
        try:
            webbrowser.open("https://github.com/james-beans/Nota/issues")
            self.update_status(f"Opened link in browser.")
        except Exception:
            self.update_status("401::Error::Link failed.")

if __name__ == "__main__":
    root = tk.Tk()
    app = WordNotesApp(root)
    root.mainloop()