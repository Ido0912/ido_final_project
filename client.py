import ssl
import socket

# כתובת השרת
HOST = '127.0.0.1'
PORT = 8443


# יצירת סוקט TLS מאובטח
def create_tls_client(host, port):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

    # ציון מיקום התעודה של השרת
    context.load_verify_locations('C:\\Users\\reuve\\PycharmProjects\\pythonProject30\\server.crt')

    # שימוש ב-TLS
    client_socket = socket.create_connection((host, port))
    secure_socket = context.wrap_socket(client_socket, server_hostname=host)
    return secure_socket



# הפעלת הלקוח
def run_client():
    client = create_tls_client(HOST, PORT)
    client.sendall(b"Hello, TLS server!")
    data = client.recv(1024)
    print(f"Received: {data.decode()}")
    client.close()


if __name__ == "__main__":
    run_client()
