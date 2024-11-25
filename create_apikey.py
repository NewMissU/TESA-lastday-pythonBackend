import uuid
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()

#Database connection parameter
DB_USER = os.getenv("DB_USER") # ดึงข้อมูลจาก .env มาใช้งาน
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")  # ค่าเริ่มต้นคือ localhost
DB_PORT = os.getenv("DB_PORT", "5433")

print("Username : " , DB_USER)
print("Password : " , DB_PASSWORD)
print("DatabaseName : " , DB_NAME)
print("Host : " , DB_HOST)
print("Port : " , DB_PORT)

#connect to the PostgreSQL database
def connection_db():
    conn = psycopg2.connect(
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
        host = DB_HOST,
        port = DB_PORT,
    )
    return conn

#cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def create_database_table():
    # เชื่อมต่อกับฐานข้อมูล PostgreSQL
    conn = connection_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # สร้างตารางสำหรับเก็บข้อมูล API Key (หากยังไม่มี)
    cur.execute('''
    CREATE TABLE IF NOT EXISTS api_keys (
        id SERIAL PRIMARY KEY,
        api_key TEXT NOT NULL
    );
    ''')
    conn.commit()
    cur.close()
    conn.close()
    
def generate_api_key():
    return str(uuid.uuid4()) # Object to string

def store_api_key():
    api_key = generate_api_key()
    print(f"Generated API Key: {api_key}")

    # เชื่อมต่อกับฐานข้อมูล PostgreSQL
    conn = connection_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # เพิ่มข้อมูล API Key ลงในตาราง
    cur.execute('''
    INSERT INTO api_keys (api_key)
    VALUES (%s);
    ''', (api_key,))
    conn.commit()

    print(f"Stored API Key: {api_key}")

    cur.close()
    conn.close()

# เรียกใช้งานฟังก์ชัน
create_database_table() #create table
store_api_key() #insert
