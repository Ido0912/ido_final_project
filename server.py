import ssl
import socket
import threading

# יצירת מפתח ותעודה (בפועל יש ליצור אותם עם OpenSSL או כלי אחר)
CERT_FILE = "server.crt"
KEY_FILE = "server.key"

# יצירת סוקט TLS מאובטח
def create_tls_server(host='127.0.0.1', port=8443):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    # יצירת סוקט TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    # עטיפת הסוקט ב-TLS
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    print(f"Server is listening on {host}:{port}")
    return secure_socket

# טיפול בחיבור לקוח
def handle_client(conn, addr):
    print(f"Connection established with {addr}")
    while True:
        try:
            data = conn.recv(1024)
            if not data:
                break
            print(f"Received: {data.decode()}")
            conn.sendall(b"Hello, TLS client!")
        except Exception as e:
            print(f"Error: {e}")
            break
    conn.close()

# הפעלת השרת
def run_server():
    server = create_tls_server()
    while True:
        conn, addr = server.accept()
        # יצירת thread חדש עבור כל חיבור
        client_thread = threading.Thread(target=handle_client, args=(conn, addr))
        client_thread.start()

if __name__ == "__main__":
    run_server()
