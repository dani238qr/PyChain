import json
import hashlib
from getpass import getpass
from pathlib import Path
from cryptography.fernet import Fernet
from ecdsa import SECP256k1, SigningKey, VerifyingKey


def derive_key(password: str) -> bytes:
    return hashlib.sha256(password.encode()).digest()


def encrypt_private_key(private_key_bytes: bytes, password: str) -> bytes:
    key = derive_key(password)
    fernet = Fernet(Fernet.generate_key())
    import base64
    key_base64 = base64.urlsafe_b64encode(key)
    fernet = Fernet(key_base64)
    return fernet.encrypt(private_key_bytes)


def decrypt_private_key(encrypted: bytes, password: str) -> bytes:
    key = derive_key(password)
    import base64
    key_base64 = base64.urlsafe_b64encode(key)
    fernet = Fernet(key_base64)
    return fernet.decrypt(encrypted)


class Wallet:
    def __init__(self, sk: SigningKey = None):
        if sk is None:
            self._sk = SigningKey.generate(curve=SECP256k1)
        else:
            self._sk = sk
        self._vk: VerifyingKey = self._sk.get_verifying_key()
        self.address: str = self._derive_address()

    def _derive_address(self) -> str:
        pub_bytes = self._vk.to_string()
        digest = hashlib.sha256(pub_bytes).digest()
        return digest[:20].hex()

    @property
    def public_key_hex(self) -> str:
        return self._vk.to_string().hex()

    def sign(self, payload: bytes) -> str:
        return self._sk.sign(payload).hex()

    def private_key_bytes(self) -> bytes:
        return self._sk.to_string()

    def __repr__(self):
        return f"<Wallet {self.address[:10]}…>"


def save_wallet(name, email, wallet: Wallet, password, filename="wallets.json"):
    # Encrypt private key
    encrypted_sk = encrypt_private_key(wallet.private_key_bytes(), password).hex()
    data = {
        "name": name,
        "email": email,
        "address": wallet.address,
        "public_key": wallet.public_key_hex,
        "encrypted_private_key": encrypted_sk,
    }

    # Load
    wallets = []
    if Path(filename).exists():
        with open(filename, "r") as f:
            wallets = json.load(f)

    # Append
    wallets.append(data)
    with open(filename, "w") as f:
        json.dump(wallets, f, indent=4)
    print(f"Wallet saved with address: {wallet.address}")


def load_wallet(address, password, filename="wallets.json") -> Wallet:
    if not Path(filename).exists():
        raise FileNotFoundError("No wallets saved yet!")

    with open(filename, "r") as f:
        wallets = json.load(f)

    for w in wallets:
        if w["address"] == address:
            encrypted_sk_bytes = bytes.fromhex(w["encrypted_private_key"])
            try:
                sk_bytes = decrypt_private_key(encrypted_sk_bytes, password)
                sk = SigningKey.from_string(sk_bytes, curve=SECP256k1)
                wallet = Wallet(sk)
                print(f"Wallet {address} loaded successfully.")
                return wallet
            except Exception as e:
                raise ValueError("Incorrect password or corrupted key.") from e

    raise ValueError("Wallet address not found.")


def main():
    print("=== Create a new wallet ===")
    name = input("Enter your name: ")
    email = input("Enter your email: ")
    password = getpass("Enter a password to secure your wallet: ")
    password_confirm = getpass("Confirm password: ")
    if password != password_confirm:
        print("Passwords do not match!")
        return

    wallet = Wallet()
    save_wallet(name, email, wallet, password)


if __name__ == "__main__":
    main()


