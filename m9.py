import os
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import datetime
import threading

# Global variable to store the last search query
last_query = ""

def list_files(directory, max_depth=3, current_depth=0):
    files_list = []
    if current_depth > max_depth:
        return files_list
    try:
        for file in os.scandir(directory):
            if file.is_file():
                files_list.append(file)
            elif file.is_dir() and not file.name.startswith('.') and not file.is_symlink():
                files_list.extend(list_files(file.path, max_depth, current_depth + 1))
    except (PermissionError, FileNotFoundError):
        pass
    return files_list

def search_files(query, files_list):
    matching_files = []
    for file in files_list:
        if query.lower() in file.path.lower():
            matching_files.append(file)
    return matching_files

def filter_files(filter_type, files_list):
    filtered_files = []
    for file in files_list:
        if filter_type == "Everything":
            filtered_files.append(file)
        elif filter_type == "PDF" and file.name.lower().endswith(".pdf"):
            filtered_files.append(file)
        elif filter_type == "Video" and file.name.lower().endswith((".mp4", ".avi", ".mkv")):
            filtered_files.append(file)
        elif filter_type == "Audio" and file.name.lower().endswith(".mp3"):
            filtered_files.append(file)
        elif filter_type == "Photo" and file.name.lower().endswith((".jpeg", ".png", ".jpg")):
            filtered_files.append(file)
        elif filter_type == "Word" and file.name.lower().endswith(".docx"):
            filtered_files.append(file)
        elif filter_type == "Excel" and file.name.lower().endswith(".xlsx"):
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
    # Get the query from the entry
    query = query_entry.get()

    # If query is empty or hasn't changed, return
    if not query or query == last_query:
        return

    last_query = query

    # Perform search in a separate thread
    search_thread = threading.Thread(target=do_search, args=(query,))
    search_thread.start()

def do_search(query):
    files = []
    for drive in range(ord('A'), ord('Z')+1):
        drive_letter = chr(drive) + ":\\"
        files.extend(list_files(drive_letter))

    matching_files = search_files(query, files)

    # Filter files based on selected filter option
    filter_type = filter_var.get()
    filtered_files = filter_files(filter_type, matching_files)

    # Schedule the update of result_tree in the main thread
    root.after(0, update_result_tree, filtered_files)

def update_result_tree(matching_files):
    result_tree.delete(*result_tree.get_children())
    if matching_files:
        for file in matching_files:
            size_mb = round(os.path.getsize(file.path) / (1024 * 1024), 2)
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file.path)).strftime('%Y-%m-%d %H:%M:%S')
            result_tree.insert('', 'end', values=(file.name, file.path, size_mb, mod_time))
    else:
        result_tree.insert('', 'end', values=("No matching files found.", "", "", ""))

# Function to handle "New" command
def new_command():
   subprocess.Popen(["python", "m8.py"])

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
    Welcome to the SEO Tool!

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

    To perform a search, enter your query in the search bar and click the "Search" button.
    The results will be displayed in the table, and you can open files by double-clicking
    or using the right-click menu.

    Have a great time using the SEO Tool!
    """
    messagebox.showinfo("About SEO Tool", about_text)

# GUI setup
root = tk.Tk()
root.title("SEO Tool")
root.geometry("1200x800")  # Set initial window size

# Widgets
query_frame = tk.Frame(root)
query_frame.grid(row=0, column=0, padx=10, pady=5, sticky="w")

label_search = tk.Label(query_frame, text="Search Query:")
label_search.grid(row=0, column=0, padx=5, pady=5, sticky="e")

query_entry = tk.Entry(query_frame, width=30)
query_entry.grid(row=0, column=1, padx=5, pady=5)

filter_var = tk.StringVar()
filter_var.set("Everything")

filter_label = tk.Label(query_frame, text="Filter:")
filter_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

filter_options = ["Everything", "PDF", "Video", "Audio", "Photo", "Word", "Excel"]
filter_dropdown = tk.OptionMenu(query_frame, filter_var, *filter_options)
filter_dropdown.grid(row=0, column=3, padx=5, pady=5)

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
edit_menu.add_command(label="Cut")
edit_menu.add_command(label="Copy")
edit_menu.add_command(label="Paste")

# View Menu
view_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="View", menu=view_menu)
# Add your view commands here if needed

# Search Menu
search_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Search", menu=search_menu)
search_menu.add_command(label="Search Everything", command=perform_search)

# Bookmarks Menu
bookmarks_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Bookmarks", menu=bookmarks_menu)
bookmarks_menu.add_command(label="Add Bookmark", command=lambda: messagebox.showinfo("Bookmark", "Bookmark added!"))

# Tools Menu
tools_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Tools", menu=tools_menu)
tools_menu.add_command(label="Options", command=lambda: messagebox.showinfo("Options", "Options menu"))

# Help Menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=about_command)
help_menu.add_separator()
#help_menu.add_command(label="Help", command=help_command)

# Run the GUI
root.mainloop()
