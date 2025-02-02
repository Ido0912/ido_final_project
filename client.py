import ssl
import socket
import threading

# כתובת השרת
HOST = '127.0.0.1'
PORT = 8443


class SecureClient:
    def __init__(self, host, port, cert_path):
        self.host = host
        self.port = port
        self.important = ""
        self.cert_path = cert_path
        self.client_socket = None
        self.secure_socket = None

    # יצירת סוקט TLS מאובטח
    def create_tls_client(self):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # ציון מיקום התעודה של השרת
        context.load_verify_locations(self.cert_path)

        # שימוש ב-TLS
        self.client_socket = socket.create_connection((self.host, self.port))
        self.secure_socket = context.wrap_socket(self.client_socket, server_hostname=self.host)

    def set_import(self):
        self.important = ""

    # טיפול בקבלת נתונים מהשרת
    def receive_data(self):
        while True:
            data = self.secure_socket.recv(1024)
            if not data:
                break
            if data != "Hello, TLS client!":
                self.important = data
            print(f"Received: {data.decode()}")

    # שליחת הודעה לשרת
    def send_message(self, message):
        self.secure_socket.sendall(message.encode())

    # הפעלת הלקוח
    def run(self):
        self.create_tls_client()

        # התחלת thread שמאזין למידע מהשרת
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()

if __name__ == "__main__":
    client = SecureClient(HOST, PORT, 'C:\\Users\\reuve\\PycharmProjects\\pythonProject30\\server.crt')
    client.run()

    # כאן אפשר לשלוח הודעות כאשר רוצים
    message = "insert facebook ido 12345"
    client.send_message(message)
