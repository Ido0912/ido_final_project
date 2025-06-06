import ssl
import socket
import threading


class SecureClient:
    def __init__(self, host, port, cert_path):
        self.host = host
        self.port = port
        self.important = ""
        self.cert_path = cert_path
        self.client_socket = None
        self.secure_socket = None

    def create_tls_client(self):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(self.cert_path)
        self.client_socket = socket.create_connection((self.host, self.port))
        self.secure_socket = context.wrap_socket(self.client_socket, server_hostname=self.host)

    def set_import(self):
        self.important = ""

    def receive_data(self):
        while True:
            data = self.secure_socket.recv(1024)
            if not data:
                break
            if data != "Hello, TLS client!":
                self.important = data
            print(f"Received: {data.decode()}")

    def send_message(self, message):
        self.secure_socket.sendall(message.encode())

    def run(self):
        self.create_tls_client()
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()

