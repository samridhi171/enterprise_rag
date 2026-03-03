import pandas as pd
import sqlite3

print("⏳ Starting database migration...")

try:
    # 1. Read your existing CSV
    df = pd.read_csv("data.csv")
    
    # 2. Create and connect to a new local SQL database
    # (This will automatically create a file called 'enterprise.db')
    conn = sqlite3.connect("enterprise.db")
    
    # 3. Push the data into a new SQL table called 'company_data'
    df.to_sql("company_data", conn, if_exists="replace", index=False)
    
    print("✅ Success! Your CSV has been converted into an SQLite database (enterprise.db).")
    
    # Close the connection
    conn.close()

except FileNotFoundError:
    print("⚠️ Error: Could not find 'data.csv'. Make sure it is in the same folder.")
except Exception as e:
    print(f"⚠️ An error occurred: {e}")