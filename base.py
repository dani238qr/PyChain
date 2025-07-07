import hashlib
import time

import json
from pathlib import Path

def load_wallet_name_address_map(filename="wallets.json"):
    if not Path(filename).exists():
        raise FileNotFoundError(
            f"\n\n!!!!\n'{filename}' not found.\n"
            "Please run 'wallet_manager.py' to create at least two users before running this script.\n!!!\n\n"
        )

    with open(filename, "r") as f:
        wallets = json.load(f)

    if len(wallets) < 2:
        raise ValueError(
            f"\n\nAt least two wallets are required for transactions. Only {len(wallets)} found.\n"
            "Please create more users using 'wallet_manager.py'.\n\n"
        )

    return {w["name"].lower(): w["address"] for w in wallets}

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        value = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
        return hashlib.sha256(value.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block", "0")

    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = Block(len(self.chain), data, prev_block.hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                print("Invalid hash at block", i)
                return False

            if current.previous_hash != previous.hash:
                print("Invalid previous hash at block", i)
                return False

        return True

# Example use
if __name__ == "__main__":
    bc = Blockchain()

    name_to_address = load_wallet_name_address_map()

    # Example transaction:
    sender = input("Sender name: ").strip().lower()
    recipient = input("Recipient name: ").strip().lower()
    amount = input("Amount: ").strip()



    if sender not in name_to_address or recipient not in name_to_address:
        print("One or both wallet names not found in wallets.json")
    else:
        tx = f"{name_to_address[sender]} pays {name_to_address[recipient]} {amount} coins"
        bc.add_block(tx)

    # Print chain
    for block in bc.chain:
        print(f"Block {block.index} | Hash: {block.hash}")
        print(f"   Data: {block.data}")
        print(f"   Prev: {block.previous_hash}\n")

    print("Blockchain valid:", bc.is_chain_valid())

