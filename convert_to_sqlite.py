import os
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

# Gunakan URL dari .env jika ada, atau default local MySQL
mysql_url = os.getenv('DW_DATABASE_URL', 'mysql+pymysql://root:@localhost/dw_hospitality')

# Path untuk file database SQLite baru
sqlite_dir = os.path.join(os.getcwd(), 'instance')
if not os.path.exists(sqlite_dir):
    os.makedirs(sqlite_dir)
sqlite_path = os.path.join(sqlite_dir, 'dw_hospitality.db')
sqlite_url = f"sqlite:///{sqlite_path.replace(os.sep, '/')}"

print(f"Connecting to source MySQL: {mysql_url}")
print(f"Connecting to target SQLite: {sqlite_url}")

try:
    mysql_engine = create_engine(mysql_url)
    sqlite_engine = create_engine(sqlite_url)
    
    # Test connection
    with mysql_engine.connect() as conn:
        print("Successfully connected to MySQL!")
except Exception as e:
    print(f"Error establishing engine connection: {e}")
    print("Pastikan XAMPP/Laragon/MySQL lokal Anda sedang aktif.")
    exit(1)

tables = [
    'dim_time',
    'dim_guest',
    'dim_hotel',
    'dim_room',
    'dim_booking_channel',
    'fact_reservation'
]

print("Starting conversion...")
try:
    for table in tables:
        print(f"Reading table '{table}' from MySQL...")
        df = pd.read_sql_table(table, mysql_engine)
        print(f"Found {len(df)} rows. Writing to SQLite...")
        df.to_sql(table, sqlite_engine, if_exists='replace', index=False)
        print(f"Successfully migrated table '{table}'!")
    
    print("\nSUCCESS! All tables and data have been migrated to SQLite.")
    print(f"Database file located at: {sqlite_path}")
    print(f"File size: {os.path.getsize(sqlite_path) / (1024*1024):.2f} MB")
    
except Exception as e:
    print(f"Error during migration: {e}")
    exit(1)
