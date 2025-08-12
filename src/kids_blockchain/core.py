
import hashlib
import json
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional

@dataclass
class Transaction:
    sender: str
    recipient: str
    amount: float
    note: str = ""
    timestamp: str = ""

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d):
        return Transaction(**d)

@dataclass
class Block:
    index: int
    timestamp: str
    transactions: List[Transaction]
    previous_hash: str
    nonce: int
    hash: str

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
        }

    @staticmethod
    def from_dict(d):
        return Block(
            index=d["index"],
            timestamp=d["timestamp"],
            transactions=[Transaction.from_dict(t) for t in d["transactions"]],
            previous_hash=d["previous_hash"],
            nonce=d["nonce"],
            hash=d["hash"]
        )

class Blockchain:
    def __init__(self, difficulty: int = 2, reward: float = 10.0):
        self.chain: List[Block] = []
        self.pending: List[Transaction] = []
        self.users = set()
        self.difficulty = max(0, int(difficulty))
        self.reward = float(reward)
        self._create_genesis()

    def _create_genesis(self):
        genesis_tx = Transaction(sender="SYSTEM", recipient="GENESIS", amount=0.0, note="Genesis", timestamp=self._now())
        block = self._new_block(previous_hash="0"*64, transactions=[genesis_tx])
        self.chain.append(block)

    def _now(self) -> str:
        return datetime.utcnow().isoformat(timespec="seconds") + "Z"

    def _hash_block(self, index: int, timestamp: str, transactions: List[Transaction], previous_hash: str, nonce: int) -> str:
        tx_json = json.dumps([t.to_dict() for t in transactions], sort_keys=True)
        block_string = f"{index}|{timestamp}|{tx_json}|{previous_hash}|{nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def _new_block(self, previous_hash: str, transactions: List[Transaction]) -> Block:
        index = len(self.chain)
        timestamp = self._now()
        nonce = 0
        # compute initial hash (without PoW); mining adjusts it
        block_hash = self._hash_block(index, timestamp, transactions, previous_hash, nonce)
        return Block(index, timestamp, transactions, previous_hash, nonce, block_hash)

    def add_user(self, name: str) -> bool:
        name = name.strip()
        if not name or name.upper() == "SYSTEM":
            return False
        if name in self.users:
            return False
        self.users.add(name)
        return True

    def add_transaction(self, sender: str, recipient: str, amount: float, note: str = "") -> Optional[str]:
        try:
            amount = float(amount)
        except ValueError:
            return "Amount must be a number."
        if amount <= 0:
            return "Amount must be positive."
        if sender != "SYSTEM" and sender not in self.users:
            return f"Unknown sender '{sender}'."
        if recipient not in self.users and recipient != "GENESIS":
            return f"Unknown recipient '{recipient}'."
        # For teaching: allow SYSTEM "faucet" mints, else check balance
        if sender != "SYSTEM":
            if self.get_balance(sender) < amount:
                return f"Insufficient funds: {sender} has {self.get_balance(sender)}."
        tx = Transaction(sender=sender, recipient=recipient, amount=amount, note=note, timestamp=self._now())
        self.pending.append(tx)
        return None

    def mine(self, miner: str) -> Block:
        if miner not in self.users:
            raise ValueError("Miner must be a known user.")
        # Add mining reward as a pending transaction
        reward_tx = Transaction(sender="SYSTEM", recipient=miner, amount=self.reward, note="Mining reward", timestamp=self._now())
        txs = self.pending + [reward_tx]
        previous_hash = self.chain[-1].hash
        block = self._new_block(previous_hash, txs)
        target_prefix = "0" * self.difficulty
        # Proof-of-work: find a nonce so that hash starts with N zeros
        while not block.hash.startswith(target_prefix):
            block.nonce += 1
            block.hash = self._hash_block(block.index, block.timestamp, block.transactions, block.previous_hash, block.nonce)
        # Confirm: move to chain and clear pending
        self.chain.append(block)
        self.pending = []
        return block

    def get_balance(self, name: str) -> float:
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == name:
                    balance -= tx.amount
                if tx.recipient == name:
                    balance += tx.amount
        # pending also affect spendability (simple model)
        for tx in self.pending:
            if tx.sender == name:
                balance -= tx.amount
        return round(balance, 8)

    def to_dict(self):
        return {
            "difficulty": self.difficulty,
            "reward": self.reward,
            "users": sorted(self.users),
            "pending": [t.to_dict() for t in self.pending],
            "chain": [b.to_dict() for b in self.chain],
        }

    @staticmethod
    def from_dict(d):
        bc = Blockchain(difficulty=d.get("difficulty", 2), reward=d.get("reward", 10.0))
        bc.users = set(d.get("users", []))
        bc.pending = [Transaction.from_dict(t) for t in d.get("pending", [])]
        bc.chain = [Block.from_dict(b) for b in d.get("chain", [])]
        return bc
