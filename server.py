import ssl
import socket
import threading
import sqlite3
from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Paths to your certificate and key files
CERT_FILE = "server.crt"
KEY_FILE = "server.key"
server_running = True

# Load the encryption key from the key file
def load_encryption_key():
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read(32)  # Use the first 32 bytes as the AES key


AES_KEY = load_encryption_key()


# Encrypt data using AES
def encrypt_data(plain_text):
    backend = default_backend()
    iv = b'\x00' * 16  # Static IV (for simplicity, should be random in production)
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=backend)
    encryptor = cipher.encryptor()
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode()) + padder.finalize()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted


# Decrypt data using AES
def decrypt_data(encrypted_data):
    backend = default_backend()
    iv = b'\x00' * 16  # Same IV as encryption
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    unpadder = padding.PKCS7(128).unpadder()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    return decrypted.decode()


# Initialize database
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


# Handle SQL queries
# Handle SQL queries
def handle_sql_query(message, conn):
    connection = sqlite3.connect("safe.db")
    cursor = connection.cursor()

    try:
        command = message.split()[0].lower()  # Extract the command (e.g., insert, update, delete, show, send)
        params = message.split()[1:]  # Extract the parameters after the command

        if command == "insert":
            # Validate input for insert
            if len(params) < 3:
                conn.sendall(b"Insert failed: Missing required parameters (Content, Username, Password)\n")
                return

            # Encrypt the parameters
            encrypted_content = encrypt_data(params[0])
            encrypted_username = encrypt_data(params[1])
            encrypted_password = encrypt_data(params[2])

            # Insert query
            query = "INSERT INTO safe (Content, Username, Password, \"Last password mod\") VALUES (?, ?, ?, ?)"
            cursor.execute(query, (encrypted_content, encrypted_username, encrypted_password, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.sendall(b"Insert successful\n")

        elif command == "update":
            if len(params) < 3:
                conn.sendall(b"Update failed: Missing required parameters (Content, Column, New Value)\n")
                return

            content, column, new_value = params
            encrypted_content = encrypt_data(content)

            # Check if content exists
            cursor.execute("SELECT * FROM safe WHERE Content = ?", (encrypted_content,))
            if not cursor.fetchone():
                conn.sendall(b"Update failed: Content not found\n")
                return

            if column == "password":
                encrypted_new_value = encrypt_data(new_value)
                query = f"UPDATE safe SET Password = ?, \"Last password mod\" = ? WHERE Content = ?"
                cursor.execute(query, (encrypted_new_value, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), encrypted_content))
            elif column == "username":
                encrypted_new_value = encrypt_data(new_value)
                query = f"UPDATE safe SET Username = ? WHERE Content = ?"
                cursor.execute(query, (encrypted_new_value, encrypted_content))
            else:
                conn.sendall(b"Update failed: Unknown column\n")
                return

            conn.sendall(b"Update successful\n")

        elif command == "delete":
            if len(params) != 1:
                conn.sendall(b"Delete failed: Missing required parameter (Content)\n")
                return

            encrypted_content = encrypt_data(params[0])
            cursor.execute("SELECT * FROM safe WHERE Content = ?", (encrypted_content,))
            if not cursor.fetchone():
                conn.sendall(b"Delete failed: Content not found\n")
                return

            query = "DELETE FROM safe WHERE Content = ?"
            cursor.execute(query, (encrypted_content,))
            conn.sendall(b"Delete successful\n")

        elif command == "show":
            if len(params) != 2:
                conn.sendall(b"Show failed: Missing required parameters (Content, Column)\n")
                return

            encrypted_content = encrypt_data(params[0])
            column = params[1]

            query = f"SELECT {column} FROM safe WHERE Content = ?"
            cursor.execute(query, (encrypted_content,))
            result = cursor.fetchone()
            if result:
                decrypted_result = decrypt_data(result[0])
                conn.sendall(f"{decrypted_result}\n".encode())
            else:
                conn.sendall(b"No data found\n")

        elif command == "send":
            # Handle 'send' to return all content names
            cursor.execute("SELECT Content FROM safe")
            rows = cursor.fetchall()
            if rows:
                content_names = [decrypt_data(row[0]) for row in rows]
                response = "Content Names:\n" + "\n".join(content_names) + "\n"
                conn.sendall(response.encode())
            else:
                conn.sendall(b"No content found\n")

        else:
            conn.sendall(b"Unknown command\n")

        connection.commit()
    except sqlite3.Error as e:
        error_msg = f"Database error: {e}\n"
        conn.sendall(error_msg.encode())
    except Exception as e:
        error_msg = f"Error: {e}\n"
        conn.sendall(error_msg.encode())
    finally:
        connection.close()



# Handle client connections
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
                print("Shutdown command received. Stopping server...")
                server_running = False
                break

            handle_sql_query(decoded_data, conn)
        except Exception as e:
            error_msg = f"Error: {e}\n"
            conn.sendall(error_msg.encode())
            break
    conn.close()


# Create a secure TLS server
def create_tls_server(host='127.0.0.1', port=8443):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    secure_socket = context.wrap_socket(server_socket, server_side=True)
    print(f"Server is listening on {host}:{port}")
    return secure_socket


# Run the server
def run_server():
    global server_running
    initialize_database()  # Ensure the database is initialized before accepting connections
    server = create_tls_server()
    while server_running:
        try:
            server.settimeout(1)  # Allow periodic checks of the server_running flag
            conn, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Server error: {e}")
            break
    print("Server shutting down...")
    server.close()


if __name__ == "__main__":
    run_server()
