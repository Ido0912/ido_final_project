import ssl
import socket
import threading

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

# טיפול בקבלת נתונים מהשרת
def receive_data(client_socket):
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f"Received: {data.decode()}")

# הפעלת הלקוח
def run_client():
    client = create_tls_client(HOST, PORT)

    # התחלת thread שמאזין למידע מהשרת
    receive_thread = threading.Thread(target=receive_data, args=(client,))
    receive_thread.start()

    # שליחת נתונים לשרת
    while True:
        message = input("Enter message to send: ")
        client.sendall(message.encode())
        if message.lower() == "exit":
            break

    client.close()

if __name__ == "__main__":
    run_client()
