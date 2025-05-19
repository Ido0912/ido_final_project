import ssl
import socket
import threading
import sqlite3
from datetime import datetime
from encryption.aes import AESEncryption

CERT_FILE = "keys/server.crt"
KEY_FILE = "keys/server.key"
server_running = True
aes = AESEncryption(KEY_FILE)


def initialize_database():
    connection = sqlite3.connect("safe.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS safe (
            Content BLOB NOT NULL,
            Username BLOB NOT NULL,
            Password BLOB NOT NULL,
            "Last password mod" TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


def handle_sql_query(message, conn):
    connection = sqlite3.connect("safe.db")
    cursor = connection.cursor()
    try:
        command = message.split()[0].lower()
        params = message.split()[1:]

        if command == "insert":
            if len(params) < 3:
                conn.sendall(b"Insert failed: Missing parameters\n")
                return
            encrypted_content = aes.encrypt(params[0])
            encrypted_username = aes.encrypt(params[1])
            encrypted_password = aes.encrypt(params[2])
            query = "INSERT INTO safe (Content, Username, Password, \"Last password mod\") VALUES (?, ?, ?, ?)"
            cursor.execute(query, (encrypted_content, encrypted_username, encrypted_password, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.sendall(b"Insert successful\n")

        elif command == "update":
            if len(params) < 3:
                conn.sendall(b"Update failed: Missing parameters\n")
                return
            content, column, new_value = params
            encrypted_content = aes.encrypt(content)
            if column == "password" or column == "username":
                encrypted_new_value = aes.encrypt(new_value)
                query = f"UPDATE safe SET {column} = ?, \"Last password mod\" = ? WHERE Content = ?"
                cursor.execute(query, (encrypted_new_value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), encrypted_content))
            else:
                conn.sendall(b"Update failed: Unknown column\n")
                return
            conn.sendall(b"Update successful\n")

        elif command == "delete":
            if len(params) != 1:
                conn.sendall(b"Delete failed: Missing parameter\n")
                return
            encrypted_content = aes.encrypt(params[0])
            cursor.execute("DELETE FROM safe WHERE Content = ?", (encrypted_content,))
            conn.sendall(b"Delete successful\n")

        elif command == "show":
            if len(params) != 2:
                conn.sendall(b"Show failed: Missing parameters\n")
                return
            encrypted_content = aes.encrypt(params[0])
            column = params[1]
            query = f"SELECT {column} FROM safe WHERE Content = ?"
            cursor.execute(query, (encrypted_content,))
            result = cursor.fetchone()
            if result:
                decrypted_result = aes.decrypt(result[0])
                conn.sendall(f"{decrypted_result}\n".encode())
            else:
                conn.sendall(b"No data found\n")

        elif command == "send":
            cursor.execute("SELECT Content FROM safe")
            rows = cursor.fetchall()
            if rows:
                content_names = [aes.decrypt(row[0]) for row in rows]
                response = "Content Names:\n" + "\n".join(content_names) + "\n"
                conn.sendall(response.encode())
            else:
                conn.sendall(b"No content found\n")

        else:
            conn.sendall(b"Unknown command\n")

        connection.commit()
    except sqlite3.Error as e:
        conn.sendall(f"Database error: {e}\n".encode())
    except Exception as e:
        conn.sendall(f"Error: {e}\n".encode())
    finally:
        connection.close()


def handle_client(conn, addr):
    global server_running
    print(f"Connection established with {addr}")
    conn.sendall(b"Hello, TLS client!\n")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            decoded_data = data.decode().strip()
            print(f"Received: {decoded_data}")
            if decoded_data == "---":
                server_running = False
                break
            handle_sql_query(decoded_data, conn)
        except Exception as e:
            conn.sendall(f"Error: {e}\n".encode())
            break
    conn.close()


def create_tls_server(host='127.0.0.1', port=8443):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    print(f"Server is listening on {host}:{port}")
    return secure_socket


def run_server():
    global server_running
    initialize_database()
    server = create_tls_server()
    while server_running:
        try:
            server.settimeout(1)
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Server error: {e}")
            break
    print("Server shutting down...")
    server.close()


if __name__ == "__main__":
    run_server()
