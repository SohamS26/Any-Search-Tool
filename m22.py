import os
import subprocess
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import datetime
import threading
import webbrowser
import qrcode
from PIL import Image, ImageTk
import zipfile
from collections import deque

# Global variable to store the last search query
last_query = ""

# Global variable to store the file index
file_index = {}

# Function to index files
def index_files(directory, max_depth=20, current_depth=0):
    if current_depth > max_depth:
        return
    try:
        for file in os.scandir(directory):
            if file.is_file():
                file_info = {
                    "name": file.name,
                    "path": file.path,
                    "size_mb": round(file.stat().st_size / (1024 * 1024), 2),
                    "mod_time": datetime.datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                }
                file_index[file.path] = file_info
            elif file.is_dir() and not file.name.startswith('.') and not file.is_symlink():
                index_files(file.path, max_depth, current_depth + 1)
    except (PermissionError, FileNotFoundError):
        pass

def search_files(query, search_directory=None):
    matching_files = []
    query_lower = query.lower()
    if search_directory:
        search_directory = os.path.normpath(search_directory)
        for path, file_info in file_index.items():
            if query_lower in path.lower() and os.path.normpath(path).startswith(search_directory):
                matching_files.append(file_info)
    else:
        for path, file_info in file_index.items():
            if query_lower in path.lower():
                matching_files.append(file_info)
    return matching_files

def filter_files(filter_type, files_list):
    filtered_files = []
    for file in files_list:
        if filter_type == "Everything":
            filtered_files.append(file)
        elif filter_type == "PDF" and file['name'].lower().endswith(".pdf"):
            filtered_files.append(file)
        elif filter_type == "Video" and file['name'].lower().endswith((".mp4", ".avi", ".mkv")):
            filtered_files.append(file)
        elif filter_type == "Audio" and file['name'].lower().endswith(".mp3"):
            filtered_files.append(file)
        elif filter_type == "Photo" and file['name'].lower().endswith((".jpeg", ".png", ".jpg")):
            filtered_files.append(file)
        elif filter_type == "Word" and file['name'].lower().endswith(".docx"):
            filtered_files.append(file)
        elif filter_type == "Excel" and file['name'].lower().endswith(".xlsx"):
            filtered_files.append(file)
    return filtered_files


def open_selected_file(event):
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        if event.num == 1:  # Left-click
            subprocess.Popen(["start", " ", selected_file[1]], shell=True)
        elif event.num == 3:  # Right-click
            subprocess.Popen(["explorer", os.path.dirname(selected_file[1])])

def perform_search(event=None):
    global last_query
    query = query_entry.get()
    if not query or query == last_query:
        return
    last_query = query
    search_directory = search_entry.get() or None
    search_thread = threading.Thread(target=do_search, args=(query, search_directory))
    search_thread.start()

def do_search(query, search_directory):
    matching_files = search_files(query, search_directory)
    filter_type = filter_var.get()
    filtered_files = filter_files(filter_type, matching_files)
    root.after(0, update_result_tree, filtered_files)

def update_result_tree(matching_files):
    result_tree.delete(*result_tree.get_children())
    if matching_files:
        for file in matching_files:
            result_tree.insert('', 'end', values=(file['name'], file['path'], file['size_mb'], file['mod_time']))
    else:
        result_tree.insert('', 'end', values=("No matching files found.", "", "", ""))

def initial_indexing():
    search_directory = search_entry.get()
    search_depth = depth_scale.get()
    if search_directory and os.path.isdir(search_directory):
        index_files(search_directory, max_depth=search_depth)
    else:
        for drive in range(ord('A'), ord('Z')+1):
            drive_letter = chr(drive) + ":\\"
            if os.path.exists(drive_letter):
                index_files(drive_letter, max_depth=search_depth)

# ... (rest of the code remains the same) ...
# Function to handle "New" command
def new_command():
    subprocess.Popen(["python", "m22.py"])

# Function to handle "Open" command
def open_command():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        subprocess.Popen(["start", " ", selected_file[1]], shell=True)

# Function to handle "Exit" command
def exit_command():
    root.destroy()

# Function to handle "About" command
def about_command():
    about_text = """
    Welcome to the AnySearch Tool!

    This tool allows you to search for files on your computer.
    You can perform a search using the search bar, and the results
    will be displayed in a table format below.

    Menu Bar Commands:
    - File: New, Open, Exit
    - Edit: Cut, Copy, Paste
    - View: Toggle Hidden Files
    - Search: Search Everything
    - Bookmarks: Add Bookmark
    - Tools: Options
    - Help: About

    The Developers are Aaditya Sirsath, Ayush Ther, Ayush Shirbhate, Jay Gulhane, Mayur Uparikar, Soham Sawalakhe!!!

    Have a great time using the AnySearch Tool!
    """
    messagebox.showinfo("About AnySearch Tool", about_text)

# Function to handle "Cut" command
def cut_command():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        root.clipboard_clear()
        root.clipboard_append(selected_file[1])

# Function to handle "Copy" command
def copy_command():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        root.clipboard_clear()
        root.clipboard_append(selected_file[1])

# Function to handle "Paste" command
def paste_command():
    query_entry.delete(0, 'end')
    query_entry.insert('end', root.clipboard_get())

# Function to toggle hidden files visibility
def toggle_hidden_files():
    pass  # Implement this function to toggle visibility of hidden files

# Define a global variable to store bookmarks
bookmarks = []

# Function to add a bookmark
def add_bookmark():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        bookmarks.append(selected_file)
        messagebox.showinfo("Bookmark Added", "Bookmark added successfully.")

# Function to view bookmarks
def view_bookmarks():
    if bookmarks:
        bookmarks_info = "\n".join([f"{index + 1}. {bookmark[0]}: {bookmark[1]}" for index, bookmark in enumerate(bookmarks)])
        messagebox.showinfo("Bookmarks", f"Your Bookmarks:\n\n{bookmarks_info}")
    else:
        messagebox.showinfo("Bookmarks", "You have no bookmarks yet.")

# Function to delete a bookmark
def delete_bookmark():
    if bookmarks:
        selected_index = simpledialog.askinteger("Delete Bookmark", "Enter the index of the bookmark you want to delete:")
        if selected_index and 1 <= selected_index <= len(bookmarks):
            del bookmarks[selected_index - 1]
            messagebox.showinfo("Bookmark Deleted", "Bookmark deleted successfully.")
    else:
        messagebox.showinfo("Bookmarks", "You have no bookmarks to delete.")

# Function to handle options menu
def show_options():
    messagebox.showinfo("Options", "Options menu")

# Function to change GUI theme to a professional color scheme
def change_theme():
    # Change theme to a professional color scheme
    root.tk_setPalette(background='#ECECEC', foreground='#333333', activeBackground='#CCCCCC', activeForeground='#000000')

# Function to share selected file via Gmail
def share_via_gmail():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        file_path = selected_file[1]
        webbrowser.open(f"mailto:?subject=File%20Attachment&body=Please%20find%20the%20attached%20file.&attach={file_path}")
    else:
        messagebox.showerror("Error", "No file selected.")

# Function to delete selected file
def delete_file():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        file_path = selected_file[1]
        try:
            os.remove(file_path)
            messagebox.showinfo("Success", "File deleted successfully.")
            perform_search()  # Refresh search results after deletion
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete file: {e}")
    else:
        messagebox.showerror("Error", "No file selected.")

# Function to rename selected file
def rename_file():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        source_file = selected_file[1]
        new_name = filedialog.asksaveasfilename(title="Enter New Name", initialfile=selected_file[0])
        if new_name:
            try:
                os.rename(source_file, new_name)
                messagebox.showinfo("Success", "File renamed successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Error renaming file: {e}")

# Function to copy selected file to a destination directory
def copy_file():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        file_path = selected_file[1]
        destination_folder = filedialog.askdirectory(title="Select Destination Folder")
        if destination_folder:
            try:
                shutil.copy(file_path, destination_folder)
                messagebox.showinfo("Success", "File copied successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to copy file: {e}")
    else:
        messagebox.showerror("Error", "No file selected.")

# Function to move selected file to a destination directory
def move_file():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        file_path = selected_file[1]
        destination_folder = filedialog.askdirectory(title="Select Destination Folder")
        if destination_folder:
            try:
                shutil.move(file_path, destination_folder)
                messagebox.showinfo("Success", "File moved successfully.")
                perform_search()  # Refresh search results after moving
            except Exception as e:
                messagebox.showerror("Error", f"Failed to move file: {e}")
    else:
        messagebox.showerror("Error", "No file selected.")

# Function to create a new folder
def create_new_folder():
    destination_folder = filedialog.askdirectory(title="Select Destination Folder")
    if destination_folder:
        new_folder_name = simpledialog.askstring("New Folder", "Enter the name of the new folder:")
        if new_folder_name:
            new_folder_path = os.path.join(destination_folder, new_folder_name)
            try:
                os.mkdir(new_folder_path)
                messagebox.showinfo("Success", "Folder created successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create folder: {e}")

# Function to analyze disk usage of a directory
def analyze_disk_usage():
    directory = filedialog.askdirectory(initialdir="/", title="Select Directory to Analyze")
    if directory:
        total_size = 0
        try:
            for root_dir, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    total_size += os.path.getsize(file_path)
            total_size_mb = total_size / (1024 * 1024)
            messagebox.showinfo("Disk Usage Analysis", f"The total disk usage of {directory} is {total_size_mb:.2f} MB.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def change_theme(default_theme='gray'):
    # Create a new window for theme customization
    theme_window = tk.Toplevel(root)
    theme_window.title("Customize Theme")
    theme_window.geometry("400x300")

    # Define variables to store selected colors
    background_color = tk.StringVar(value=default_theme)
    foreground_color = tk.StringVar()
    button_color = tk.StringVar()

    def apply_theme():
        # Get selected colors
        bg_color = background_color.get()
        fg_color = foreground_color.get()
        btn_color = button_color.get()

        # Apply selected colors to the root window
        root.configure(background=bg_color)
        root.tk_setPalette(background=bg_color, foreground=fg_color, activeBackground=btn_color, activeForeground=fg_color)

    # Create labels and color pickers for each element
    bg_label = tk.Label(theme_window, text="Background Color:")
    bg_label.grid(row=0, column=0, padx=10, pady=5)
    bg_picker = tk.ttk.Combobox(theme_window, textvariable=background_color, values=("white", "black", "gray", "blue", "green", "red"))
    bg_picker.grid(row=0, column=1, padx=10, pady=5)

    fg_label = tk.Label(theme_window, text="Foreground Color:")
    fg_label.grid(row=1, column=0, padx=10, pady=5)
    fg_picker = tk.ttk.Combobox(theme_window, textvariable=foreground_color, values=("black", "white", "gray", "blue", "green", "red"))
    fg_picker.grid(row=1, column=1, padx=10, pady=5)

    btn_label = tk.Label(theme_window, text="Button Color:")
    btn_label.grid(row=2, column=0, padx=10, pady=5)
    btn_picker = tk.ttk.Combobox(theme_window, textvariable=button_color, values=("blue", "green", "red", "yellow", "orange", "purple"))
    btn_picker.grid(row=2, column=1, padx=10, pady=5)

    apply_button = tk.Button(theme_window, text="Apply", command=apply_theme)
    apply_button.grid(row=3, columnspan=2, padx=10, pady=10)

# Function to display the contents of a text file
def preview_text_file():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        file_path = selected_file[1]
        if file_path.lower().endswith(".txt"):
            try:
                with open(file_path, 'r') as file:
                    file_contents = file.read()
                # Display file contents in a popup window
                preview_window = tk.Toplevel(root)
                preview_window.title("Text File Preview")
                preview_window.geometry("600x400")

                text_preview = tk.Text(preview_window, wrap="word")
                text_preview.insert("1.0", file_contents)
                text_preview.pack(fill="both", expand=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to preview file: {e}")
        else:
            messagebox.showinfo("Information", "This feature only supports previewing text files (*.txt).")
    else:
        messagebox.showinfo("Information", "No file selected.")

# Function to generate and display the QR code with download link
def generate_qr_code():
    selected_item = result_tree.focus()
    if selected_item:
        selected_file = result_tree.item(selected_item)['values']
        file_path = selected_file[1]

        # Generate download link for the file
        download_link = f"file://{os.path.abspath(file_path)}"

        # Generate QR code
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(download_link)
        qr.make(fit=True)

        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Display QR code image in a dialog
        qr_image.show()
    else:
        messagebox.showerror("Error", "No file selected.")


# Function to compress selected files into a zip archive
def compress_files():
    selected_items = result_tree.selection()
    if selected_items:
        # Prompt user to select destination folder
        destination_folder = filedialog.askdirectory(title="Select Destination Folder for Zip Archive")
        if destination_folder:
            # Prompt user to specify zip file name
            zip_file_name = simpledialog.askstring("Compress Files", "Enter the name of the zip file:")
            if zip_file_name:
                zip_file_path = os.path.join(destination_folder, f"{zip_file_name}.zip")
                try:
                    with zipfile.ZipFile(zip_file_path, 'w') as zip_file:
                        for item in selected_items:
                            selected_file = result_tree.item(item)['values'][1]
                            zip_file.write(selected_file, os.path.basename(selected_file))
                    messagebox.showinfo("Success", "Files compressed successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to compress files: {e}")
    else:
        messagebox.showerror("Error", "No files selected.")


# Function to handle "Compress Files" button click from the menu bar
def compress_files_menu():
    compress_files()



# GUI setup
root = tk.Tk()
root.title("AnySearch Tool")
root.geometry("1200x800")  # Set initial window size

# Set default theme to gray
change_theme(default_theme='black')

query_frame = tk.Frame(root)
query_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

label_search = tk.Label(query_frame, text="Search Query:")
label_search.grid(row=0, column=0, padx=5, pady=5, sticky="e")

query_entry = tk.Entry(query_frame, width=30)
query_entry.grid(row=0, column=1, padx=5, pady=5)

search_label = tk.Label(query_frame, text="Search Directory:")
search_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

search_entry = tk.Entry(query_frame, width=30)
search_entry.grid(row=0, column=3, padx=5, pady=5)

search_button = tk.Button(query_frame, text="Select Directory", command=lambda: select_directory())
search_button.grid(row=0, column=4, padx=5, pady=5)

def select_directory():
    # Clear existing entry
    search_entry.delete(0, 'end')
    # Insert selected directory
    search_entry.insert('end', filedialog.askdirectory())

filter_var = tk.StringVar()
filter_var.set("Everything")

filter_options = ["Everything", "PDF", "Video", "Audio", "Photo", "Word", "Excel"]
filter_dropdown = tk.OptionMenu(query_frame, filter_var, *filter_options)
filter_dropdown.grid(row=0, column=5, padx=5, pady=5)

result_tree = ttk.Treeview(root, columns=("Name", "Path", "Size (MB)", "Date Modified"), show="headings")
result_tree.heading("Name", text="Name")
result_tree.heading("Path", text="Path")
result_tree.heading("Size (MB)", text="Size (MB)")
result_tree.heading("Date Modified", text="Date Modified")

# Center-align "Size (MB)" and "Date Modified" columns
result_tree.column("Size (MB)", anchor="center")
result_tree.column("Date Modified", anchor="center")

result_tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

# Expand widgets within the grid cell
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

# Bind search function to KeyRelease event of search entry widget
query_entry.bind("<KeyRelease>", perform_search)

# Bind double click and right-click events
result_tree.bind("<Double-Button-1>", open_selected_file)
result_tree.bind("<Button-3>", open_selected_file)

# Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# File Menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_command)
file_menu.add_command(label="Open", command=open_command)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=exit_command)

# Edit Menu
edit_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut", command=cut_command)
edit_menu.add_command(label="Copy", command=copy_command)
edit_menu.add_command(label="Paste", command=paste_command)

# View Menu
view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="View", menu=view_menu)
# view_menu.add_command(label="Toggle Hidden Files")
view_menu.add_command(label="Change Theme", command=change_theme)

# # Search Menu
# search_menu = tk.Menu(menu_bar, tearoff=0)
# menu_bar.add_cascade(label="Search", menu=search_menu)
# search_menu.add_command(label="Search Everything", command=perform_search)

# Add "Bookmarks" menu to the menu bar
bookmarks_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Bookmarks", menu=bookmarks_menu)
bookmarks_menu.add_command(label="Add Bookmark", command=add_bookmark)
bookmarks_menu.add_command(label="View Bookmarks", command=view_bookmarks)
bookmarks_menu.add_command(label="Delete Bookmark", command=delete_bookmark)

# Tools Menu
tools_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Tools", menu=tools_menu)
# tools_menu.add_command(label="Options", command=show_options)

# Help Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=about_command)

# Share Menu
share_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Share", menu=share_menu)
share_menu.add_command(label="Share via Gmail", command=share_via_gmail)

# Add "File Operations" submenu to the menu bar
file_operations_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File Operations", menu=file_operations_menu)
file_operations_menu.add_command(label="Delete", command=delete_file)
file_operations_menu.add_command(label="Rename", command=rename_file)
file_operations_menu.add_command(label="Copy", command=copy_file)
file_operations_menu.add_command(label="Move", command=move_file)

# Add "New Folder" option to the "File Operations" menu
file_operations_menu.add_command(label="New Folder", command=create_new_folder)

# Add "Analyze Disk Usage" option to the "Tools" menu
tools_menu.add_command(label="Analyze Disk Usage", command=analyze_disk_usage)

# Change theme to a professional color scheme
root.tk_setPalette(background='white', foreground='black', activeBackground='#87CEEB', activeForeground='black')

# Add "Preview" button to the GUI
preview_button = tk.Button(query_frame, text="Preview", command=preview_text_file)
preview_button.grid(row=0, column=6, padx=5, pady=5)

# Add "Generate QR Code" option to the "Tools" menu
tools_menu.add_command(label="Generate QR Code", command=generate_qr_code)

# Add "Compress Files" button to the menu bar
file_operations_menu.add_command(label="Compress Files", command=compress_files_menu)

# Add a Scale widget for adjusting search depth
depth_label = tk.Label(query_frame, text="Search Depth:")
depth_label.grid(row=0, column=7, padx=5, pady=5, sticky="e")

depth_scale = tk.Scale(query_frame, from_=1, to=10, orient='horizontal')
depth_scale.set(3)  # Default depth
depth_scale.grid(row=0, column=8, padx=5, pady=5)

# Perform initial indexing in a separate thread
initial_indexing_thread = threading.Thread(target=initial_indexing)
initial_indexing_thread.start()

# Run the GUI
root.mainloop()
