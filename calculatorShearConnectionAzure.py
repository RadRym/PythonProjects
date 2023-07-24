import pyodbc
import tkinter as tk
from tkinter import ttk, messagebox

connection = None

def connect_to_database(server='steel.database.windows.net', database='steeldata',
                        username='adrianrymarz', password='rq7U9zU6P@TtRZRiwurXA',
                        driver='{ODBC Driver 17 for SQL Server}'):
    conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    try:
        conn = pyodbc.connect(conn_str)
        return conn
    except pyodbc.Error as e:
        messagebox.showerror("Błąd", f"Błąd podczas łączenia z bazą danych:\n{e}")
        return None

def get_table_names(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type='BASE TABLE';")
        table_names = [row.table_name for row in cursor.fetchall()]
        return table_names
    except pyodbc.Error as e:
        messagebox.showerror("Błąd", f"Błąd podczas pobierania nazw tabel:\n{e}")
        return []

def get_table_columns(connection, table_name):
    try:
        cursor = connection.cursor()
        cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
        columns = [column[0] for column in cursor.description]
        return columns
    except pyodbc.Error as e:
        messagebox.showerror("Błąd", f"Błąd podczas pobierania nazw kolumn:\n{e}")
        return []

def get_table_data(connection, table_name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {table_name} ORDER BY 1 OFFSET 0 ROWS FETCH NEXT 1000 ROWS ONLY")
            table_data = cursor.fetchall()
        return table_data
    except pyodbc.Error as e:
        messagebox.showerror("Błąd", f"Błąd podczas pobierania danych z tabeli {table_name}:\n{e}")
        return []

def open_new_window():
    def on_new_window_close():
        new_window.destroy()
    
    new_window = tk.Toplevel(root)
    new_window.title("Praca z bazą danych")
    new_window.geometry("600x400")
    new_window.protocol("WM_DELETE_WINDOW", on_new_window_close)

    table_names = get_table_names(connection)

    if table_names:
        tables_label = tk.Label(new_window, text="Wybierz tabelę:")
        tables_label.pack()

        table_combobox = ttk.Combobox(new_window, values=table_names, state="readonly", width=30)
        table_combobox.pack()

        table_tree = ttk.Treeview(new_window, show="headings")
        table_tree.pack(fill=tk.BOTH, expand=True)

        def adjust_treeview_columns(tree):
            for col in tree["columns"]:
                tree.column(col, minwidth=50, width=tree.column(col, "minwidth"))
            for col in tree["columns"]:
                max_len = max(tree.set(row, col) for row in tree.get_children())
                col_width = max(50, len(col) * 8, max_len * 8)
                tree.column(col, width=col_width)

        def on_table_select(event):
            selected_table = table_combobox.get()
            table_columns = get_table_columns(connection, selected_table)

            def get_table_columns_names(connection, table_name):
                try:
                    with connection.cursor() as cursor:
                        cursor.execute(f"SELECT TOP 1 * FROM {table_name}")
                        column_names = [column[0] for column in cursor.description]
                    return column_names
                except pyodbc.Error as e:
                    messagebox.showerror("Błąd", f"Błąd podczas pobierania nazw kolumn:\n{e}")
                    return []

            if table_columns:
                column_names = get_table_columns_names(connection, selected_table)

                table_tree["columns"] = table_columns[1:]
                for idx, col in enumerate(table_columns[1:], start=0):
                    table_tree.heading(col, text=column_names[idx])

                table_data = get_table_data(connection, selected_table)
                for idx, row in enumerate(table_data, start=1):
                    formatted_row = [f"{value:.2f}" if isinstance(value, float) else value for value in row[1:]]
                    table_tree.insert("", tk.END, values=[idx] + formatted_row)

                adjust_treeview_columns(table_tree)

                table_tree.xview_moveto(0)
                table_tree.xview_scroll(10, "units")
                
        table_combobox.bind("<<ComboboxSelected>>", on_table_select)

    else:
        message_label = tk.Label(new_window, text="Brak tabel w bazie danych.")
        message_label.pack()

def on_connect_button_click():
    server = server_entry.get()
    database = database_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    global connection
    connection = connect_to_database(server, database, username, password)
    if connection:
        status_label.config(text="Połączenie z bazą danych udane.", fg="green")
        open_new_window()
    else:
        status_label.config(text="Błąd połączenia z bazą danych.", fg="red")

root = tk.Tk()
root.title("Połączenie z bazą danych")
root.geometry("400x250")

server_label = tk.Label(root, text="Server:")
server_label.pack()
server_entry = tk.Entry(root, width=40)
server_entry.insert(0, 'steel.database.windows.net')
server_entry.pack()

database_label = tk.Label(root, text="Database:")
database_label.pack()
database_entry = tk.Entry(root, width=40)
database_entry.insert(0, 'steeldata')
database_entry.pack()

username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root, width=40)
username_entry.insert(0, 'adrianrymarz')
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*", width=40)
password_entry.insert(0, 'rq7U9zU6P@TtRZRiwurXA')
password_entry.pack()

connect_button = tk.Button(root, text="Połącz", command=on_connect_button_click)
connect_button.pack()

status_label = tk.Label(root, text="", fg="black")
status_label.pack()

root.mainloop()
