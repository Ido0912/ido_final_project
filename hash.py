class SHA256:
    def __init__(self):
        # אתחול קבועים פנימיים של SHA256 (K)
        self.K = [
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
            0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
            0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0x8e44a4a4, 0x1d8d2cd0, 0x3422b06a, 0x565d1d26,
            0x66d7d7ea, 0x21c0e34b, 0x8107b267, 0x273e1f1e,
            0x64a38f0f, 0x8592b24d, 0x9fae12fd, 0x1bd9adf2,
            0x423e5b6c, 0x68c08e0d, 0x59a59260, 0xe59c9b5b,
        ]
        # שמירת הערכים ההתחלתיים המקוריים של H
        self.initial_H = [
            0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
            0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
        ]

    def pad_message(self, message):
        message_bit_length = len(message) * 8
        message += b'\x80'
        while len(message) % 64 != 56:
            message += b'\x00'
        message += message_bit_length.to_bytes(8, 'big')
        return message

    def rotr(self, x, n):
        return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

    def process_block(self, block):
        w = [0] * 64
        for i in range(16):
            w[i] = int.from_bytes(block[i * 4:(i + 1) * 4], 'big')
        for i in range(16, 64):
            s0 = self.rotr(w[i - 15], 7) ^ self.rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = self.rotr(w[i - 2], 17) ^ self.rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF

        a, b, c, d, e, f, g, h = self.H
        for i in range(64):
            k = self.K[i % len(self.K)]
            S1 = self.rotr(e, 6) ^ self.rotr(e, 11) ^ self.rotr(e, 25)
            ch = (e & f) ^ (~e & g)
            temp1 = (h + S1 + ch + k + w[i]) & 0xFFFFFFFF
            S0 = self.rotr(a, 2) ^ self.rotr(a, 13) ^ self.rotr(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        self.H[0] = (self.H[0] + a) & 0xFFFFFFFF
        self.H[1] = (self.H[1] + b) & 0xFFFFFFFF
        self.H[2] = (self.H[2] + c) & 0xFFFFFFFF
        self.H[3] = (self.H[3] + d) & 0xFFFFFFFF
        self.H[4] = (self.H[4] + e) & 0xFFFFFFFF
        self.H[5] = (self.H[5] + f) & 0xFFFFFFFF
        self.H[6] = (self.H[6] + g) & 0xFFFFFFFF
        self.H[7] = (self.H[7] + h) & 0xFFFFFFFF

    def compute_hash(self, message):
        # אתחול מחדש של H
        self.H = self.initial_H[:]
        message = self.pad_message(message)
        for i in range(0, len(message), 64):
            block = message[i:i + 64]
            self.process_block(block)
        return ''.join(f'{h:08x}' for h in self.H)


# דוגמת שימוש
if __name__ == "__main__":
    sha256 = SHA256()
    text = "12345"
    for i in range(10):
        encrypted_text = sha256.compute_hash(text.encode('utf-8'))
        print(f"הטקסט המוצפן הוא: {encrypted_text}")
