import pyodbc
import pandas as pd

server = 'steel.database.windows.net'
database = 'steeldata'
username = 'adrianrymarz'
password = 'rq7U9zU6P@TtRZRiwurXA'   
driver= '{ODBC Driver 17 for SQL Server}'
conn_str = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
table_name = 'IPE'

conn = pyodbc.connect(conn_str)
if conn:
    print("Połączenie z bazą danych udane.")

excel_file = 'C:\\Users\\adria\\Desktop\\MyDB.xlsx'
sheet_name = table_name
df = pd.read_excel(excel_file, sheet_name=sheet_name)

cursor = conn.cursor()
cursor.execute(f"DELETE FROM {table_name}")

for index, row in df.iterrows():
    columns = ", ".join([f"[{col}]" for col in df.columns])
    placeholders = ", ".join(["?"] * len(df.columns))
    query = f"INSERT INTO [{table_name}] ({columns}) VALUES ({placeholders})"
    values = [value if pd.notnull(value) else None for value in row]
    cursor.execute(query, tuple(values))

conn.commit()
conn.close()