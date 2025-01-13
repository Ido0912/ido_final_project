import ssl
import socket

# יצירת מפתח ותעודה (בפועל יש ליצור אותם עם OpenSSL או כלי אחר)
CERT_FILE = "server.crt"
KEY_FILE = "server.key"


# יצירת סוקט TLS מאובטח
def create_tls_server(host='127.0.0.1', port=8443):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    # שמירת המפתח בזיכרון הווירטואלי
    with open(KEY_FILE, 'rb') as key_file:
        private_key = key_file.read()

    print("Private key loaded into virtual memory.")

    # יצירת סוקט TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    # עטיפת הסוקט ב-TLS
    secure_socket = context.wrap_socket(server_socket, server_side=True)
    print(f"Server is listening on {host}:{port}")
    return secure_socket


# הפעלת השרת
def run_server():
    server = create_tls_server()
    while True:
        conn, addr = server.accept()
        print(f"Connection established with {addr}")
        data = conn.recv(1024)
        print(f"Received: {data.decode()}")
        conn.sendall(b"Hello, TLS client!")
        conn.close()


if __name__ == "__main__":
    run_server()
