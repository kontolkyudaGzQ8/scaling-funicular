from dataclasses import dataclass

from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta
# import hashlib

@dataclass
class DatabaseConfig: 
    host: str = "localhost"
    user: str = "root"
    password: str = ""
    database: str = "km-mart"

db = SQLAlchemy()

# class Database(SQLAlchemy): 
#     def __init__(
#         self, 
#         host: str,
#         user: str,
#         password: str,
#         database: str
#     ): 
#         super().__init__()
# conn = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="km-mart"
# )
# cursor = conn.cursor(dictionary=True)

# def check_admin(username: str, password: str) -> dict | None: 
#     encoded_password = hashlib.sha1(password.encode()).hexdigest()
#     query = "SELECT * FROM admin WHERE username = %s AND password = %s"
#     cursor.execute(query, (username,encoded_password,))
#     return cursor.fetchone()

# def load_produk(): 
#     query = "SELECT * FROM produk"
#     cursor.execute(query)
#     return cursor.fetchall()

# def get_produk(prod_id: str) -> dict | None:
#     query = "SELECT * FROM produk WHERE id = %s"
#     cursor.execute(query, (prod_id,))
#     return cursor.fetchone() 

# def update_produk(prod_id: str, data: dict) -> bool: 
#     query = """
#         UPDATE produk
#         SET nama_produk = %s, harga = %s, kategori = %s, gambar = %s
#         WHERE id = %s
#     """
#     try: 
#         cursor.execute(query, (
#                 data.get('nama_produk'),
#                 data.get('harga'),
#                 data.get('kategori'),
#                 data.get('gambar'),
#                 prod_id
#         ))
#         return True
#     except Exception as e:
#         print(f"Error saat update produk: {e}")
#         return False


# def load_penjualan(): 
#     query = "SELECT * FROM penjualan"
#     cursor.execute(query)
#     return cursor.fetchall()

# def load_penjualan_chart():
#     today = datetime.today()
#     date_labels = [(today - timedelta(days=i)).strftime('%d %b') for i in reversed(range(7))]
#     date_map = {label: 0 for label in date_labels}

#     cursor.execute("SELECT tanggal FROM penjualan")
#     rows = cursor.fetchall()
#     for row in rows:
#         tgl = row['tanggal'].strftime('%d %b')
#         if tgl in date_map:
#             date_map[tgl] += 1

#     return list(date_map.keys()), list(date_map.values())
