from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend


class AESEncryption:
    def __init__(self, key_path):
        self.key = self.load_key(key_path)
        self.iv = b'\x00' * 16
        self.backend = default_backend()

    def load_key(self, key_path):
        with open(key_path, "rb") as key_file:
            return key_file.read(32)

    def encrypt(self, plain_text: str) -> bytes:
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plain_text.encode()) + padder.finalize()
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        return encrypted

    def decrypt(self, encrypted_data: bytes) -> str:
        cipher = Cipher(algorithms.AES(self.key), modes.CBC(self.iv), backend=self.backend)
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        return decrypted.decode()

