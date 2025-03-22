import hashlib
import time
import tkinter as tk
from tkinter import messagebox, Toplevel
from typing import List, Dict, Optional

class Block:
    def __init__(self, index: int, timestamp: float, transactions: List[Dict], proof: int, previous_hash: str):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.proof = proof
        self.previous_hash = previous_hash

    def to_dict(self) -> Dict:
        """Converts the block into a dictionary for easier hashing and display."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "proof": self.proof,
            "previous_hash": self.previous_hash,
        }

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        # Create the genesis block
        self.create_block(proof=1, previous_hash="0")

    def create_block(self, proof: int, previous_hash: Optional[str] = None) -> Block:
        """Creates a new block and adds it to the blockchain."""
        block = Block(
            index=len(self.chain) + 1,
            timestamp=time.time(),
            transactions=self.pending_transactions,
            proof=proof,
            previous_hash=previous_hash or self.hash(self.chain[-1])
        )
        self.pending_transactions = []
        self.chain.append(block)
        return block

    @staticmethod
    def hash(block: Block) -> str:
        """Generates a SHA-256 hash of a block."""
        block_string = str(block.to_dict()).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """Adds a new transaction to the list of pending transactions."""
        transaction = {
            "sender": sender,
            "recipient": recipient,
            "amount": amount,
        }
        self.pending_transactions.append(transaction)
        return self.last_block.index + 1

    @property
    def last_block(self) -> Block:
        return self.chain[-1]

    def proof_of_work(self, last_proof: int) -> int:
        """Simple Proof of Work Algorithm:
        - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'.
        - p is the previous proof, and p' is the new proof.
        """
        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """Validates the proof: does hash(last_proof, proof) contain 4 leading zeroes?"""
        guess = f"{last_proof}{proof}".encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

# Initialize blockchain
blockchain = Blockchain()

# Tkinter GUI Setup
root = tk.Tk()
root.title("Simple Blockchain GUI")
root.geometry("600x400")

def add_transaction_gui():
    sender = sender_entry.get()
    recipient = recipient_entry.get()
    try:
        amount = float(amount_entry.get())
        blockchain.add_transaction(sender, recipient, amount)
        messagebox.showinfo("Success", "Transaction added successfully!")
    except ValueError:
        messagebox.showerror("Error", "Invalid amount. Please enter a valid number.")
    sender_entry.delete(0, tk.END)
    recipient_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

def mine_block_gui():
    last_proof = blockchain.last_block.proof
    proof = blockchain.proof_of_work(last_proof)
    blockchain.add_transaction(sender="0", recipient="miner_address", amount=1)  # Reward for mining
    block = blockchain.create_block(proof)
    messagebox.showinfo("Success", f"Block {block.index} mined successfully!")
    display_chain()

def display_chain():
    chain_text.delete("1.0", tk.END)
    for block in blockchain.chain:
        block_info = f"""
        Block {block.index}:
        Timestamp: {time.ctime(block.timestamp)}
        Transactions: {block.transactions}
        Proof: {block.proof}
        Previous Hash: {block.previous_hash}\n
        """
        chain_text.insert(tk.END, block_info)

def view_transactions():
    """Displays a new window with all pending transactions."""
    transactions_window = Toplevel(root)
    transactions_window.title("Pending Transactions")
    transactions_window.geometry("400x300")

    if blockchain.pending_transactions:
        transactions_text = tk.Text(transactions_window, wrap="word")
        transactions_text.pack(expand=True, fill="both")
        for transaction in blockchain.pending_transactions:
            transaction_info = f"Sender: {transaction['sender']}, Recipient: {transaction['recipient']}, Amount: {transaction['amount']}\n"
            transactions_text.insert(tk.END, transaction_info)
    else:
        message = tk.Label(transactions_window, text="No pending transactions.", font=("Arial", 14))
        message.pack(pady=20)

# Transaction UI
transaction_frame = tk.Frame(root)
transaction_frame.pack(pady=10)

sender_label = tk.Label(transaction_frame, text="Sender:")
sender_label.grid(row=0, column=0)
sender_entry = tk.Entry(transaction_frame)
sender_entry.grid(row=0, column=1)

recipient_label = tk.Label(transaction_frame, text="Recipient:")
recipient_label.grid(row=1, column=0)
recipient_entry = tk.Entry(transaction_frame)
recipient_entry.grid(row=1, column=1)

amount_label = tk.Label(transaction_frame, text="Amount:")
amount_label.grid(row=2, column=0)
amount_entry = tk.Entry(transaction_frame)
amount_entry.grid(row=2, column=1)

add_transaction_button = tk.Button(transaction_frame, text="Add Transaction", command=add_transaction_gui)
add_transaction_button.grid(row=3, column=0, columnspan=2, pady=10)

# Mining UI
mine_button = tk.Button(root, text="Mine Block", command=mine_block_gui)
mine_button.pack(pady=10)

# View Transactions Button
view_transactions_button = tk.Button(root, text="View Transactions", command=view_transactions)
view_transactions_button.pack(pady=10)

# Blockchain Display UI
chain_label = tk.Label(root, text="Blockchain:")
chain_label.pack()
chain_text = tk.Text(root, height=10, width=70)
chain_text.pack()

display_chain()

# Run the Tkinter main loop
root.mainloop()
