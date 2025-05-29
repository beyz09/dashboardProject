import pyodbc
import pandas as pd

def get_connection():
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=beyz\\SQLEXPRESS;'
        'DATABASE=diabetes_db;'
        'Trusted_Connection=yes;'
    )
    return conn

def fetch_data(query):
    conn = get_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df 