import sqlite3
from datetime import datetime

conn = sqlite3.connect("vpn.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS vpn (ip_address TEXT, droplet_id TEXT, random_suffix TEXT, created_at TIMESTAMP)")
conn.commit()
conn.close()

def insert_vpn(ip_address, droplet_id, random_suffix):
    conn = sqlite3.connect("vpn.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO vpn (ip_address, droplet_id, random_suffix, created_at) VALUES (?, ?, ?, ?)", (ip_address, droplet_id, random_suffix, datetime.now()))
    conn.commit()
    conn.close()

def get_vpn():
    conn = sqlite3.connect("vpn.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vpn")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_vpn(ip_address, droplet_id, random_suffix):
    conn = sqlite3.connect("vpn.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vpn WHERE ip_address = ? AND droplet_id = ? AND random_suffix = ?", (ip_address, droplet_id, random_suffix))
    conn.commit()
    conn.close()    