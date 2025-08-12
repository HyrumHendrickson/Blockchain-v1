
import json
import shlex
from typing import Optional
from .core import Blockchain

class BlockchainShell:
    PROMPT = "> "

    def __init__(self):
        self.bc = Blockchain(difficulty=2, reward=10.0)
        self.current_user: Optional[str] = None

    # ----------------------
    # REPL
    # ----------------------
    def cmdloop(self):
        while True:
            try:
                line = input(self.PROMPT)
            except EOFError:
                print()
                break
            if not line.strip():
                continue
            self.handle(line.strip())

    def handle(self, line: str):
        try:
            parts = shlex.split(line)
        except ValueError as e:
            print(f"Parse error: {e}")
            return
        cmd = parts[0].lower()
        args = parts[1:]

        # Dispatch
        handler = getattr(self, f"do_{cmd}", None)
        if handler is None:
            print(f"Unknown command '{cmd}'. Type 'help' for a list.")
            return
        try:
            handler(*args)
        except TypeError:
            print(f"Usage error. Try: help {cmd}")
        except Exception as e:
            print(f"Error: {e}")

    # ----------------------
    # Commands
    # ----------------------
    def do_help(self, *args):
        if not args:
            print("Commands:")
            print("  help [cmd]            Show help for a command")
            print("  create_user <name>    Create a new user")
            print("  users                 List users")
            print("  login <name>          Login as user")
            print("  logout                Logout current user")
            print("  whoami                Show current user")
            print("  faucet <amount>       Mint coins from SYSTEM to yourself")
            print("  send <to> <amount> [note...]  Create a pending payment")
            print("  pending               Show pending transactions")
            print("  mine                  Mine a block (confirms pending + reward)")
            print("  difficulty [N]        Get or set PoW difficulty")
            print("  reward [AMOUNT]       Get or set mining reward")
            print("  balance [name]        Show balance (default: current user)")
            print("  chain [n]             Show last n blocks or entire chain")
            print("  save <file.json>      Save the current state to a file")
            print("  load <file.json>      Load state from a file")
            print("  exit / quit           Exit the program")
            return
        topic = args[0]
        method = getattr(self, f"help_{topic}", None)
        if method:
            method()
        else:
            print(f"No detailed help for '{topic}'.")

    def do_create_user(self, name=None):
        if not name:
            print("Usage: create_user <name>")
            return
        ok = self.bc.add_user(name)
        if ok:
            print(f"User '{name}' created.")
        else:
            print(f"Could not create user '{name}'. It may already exist or be invalid.")

    def do_users(self):
        users = sorted(self.bc.users)
        print("Users:", ", ".join(users) if users else "(none)")

    def do_login(self, name=None):
        if not name:
            print("Usage: login <name>")
            return
        if name not in self.bc.users:
            print(f"Unknown user '{name}'. Create it first with create_user.")
            return
        self.current_user = name
        print(f"Logged in as '{name}'.")

    def do_logout(self):
        self.current_user = None
        print("Logged out.")

    def do_whoami(self):
        print(self.current_user if self.current_user else "(not logged in)")

    def do_faucet(self, amount=None):
        if not self.current_user:
            print("Login first.")
            return
        if not amount:
            print("Usage: faucet <amount>")
            return
        err = self.bc.add_transaction("SYSTEM", self.current_user, amount, note="Faucet")
        if err:
            print("Error:", err)
        else:
            print(f"Added faucet of {amount} to {self.current_user}. Use 'mine' to confirm.")

    def do_send(self, to=None, amount=None, *note):
        if not self.current_user:
            print("Login first.")
            return
        if not to or amount is None:
            print("Usage: send <to> <amount> [note...]")
            return
        note_str = " ".join(note) if note else ""
        err = self.bc.add_transaction(self.current_user, to, amount, note=note_str)
        if err:
            print("Error:", err)
        else:
            print(f"Added payment {amount} from {self.current_user} to {to}. Use 'mine' to confirm.")

    def do_pending(self):
        if not self.bc.pending:
            print("(no pending transactions)")
            return
        for i, tx in enumerate(self.bc.pending, 1):
            print(f"{i}. {tx.timestamp} | {tx.sender} -> {tx.recipient} : {tx.amount}  {tx.note}")

    def do_mine(self):
        if not self.current_user:
            print("Login first.")
            return
        block = self.bc.mine(self.current_user)
        print(f"Mined block #{block.index} with {len(block.transactions)} txs. Hash: {block.hash[:16]}...")

    def do_difficulty(self, new_value=None):
        if new_value is None:
            print(f"Current difficulty: {self.bc.difficulty}")
            return
        try:
            n = int(new_value)
            if n < 0 or n > 6:
                print("Choose a small integer (0-6) for teaching purposes.")
                return
            self.bc.difficulty = n
            print(f"Difficulty set to {n}.")
        except ValueError:
            print("Usage: difficulty [N]")

    def do_reward(self, amount=None):
        if amount is None:
            print(f"Current mining reward: {self.bc.reward}")
            return
        try:
            r = float(amount)
            if r <= 0:
                print("Reward must be positive.")
                return
            self.bc.reward = r
            print(f"Mining reward set to {r}.")
        except ValueError:
            print("Usage: reward [AMOUNT]")

    def do_balance(self, name=None):
        target = name or self.current_user
        if not target:
            print("Usage: balance [name]  (default: current user)")
            return
        if target not in self.bc.users and target != "GENESIS":
            print(f"Unknown user '{target}'.")
            return
        bal = self.bc.get_balance(target)
        print(f"{target} balance: {bal}")

    def do_chain(self, n=None):
        chain = self.bc.chain
        if n is not None:
            try:
                k = int(n)
                if k < 1:
                    raise ValueError
                chain = chain[-k:]
            except ValueError:
                print("Usage: chain [n]")
                return
        for b in chain:
            print(f"# Block {b.index}  |  time {b.timestamp}")
            print(f"  prev: {b.previous_hash}")
            print(f"  hash: {b.hash}")
            print(f"  nonce: {b.nonce}")
            for i, tx in enumerate(b.transactions, 1):
                print(f"    {i}) {tx.timestamp}  {tx.sender} -> {tx.recipient} : {tx.amount}  {tx.note}")
            print()

    def do_save(self, path=None):
        if not path:
            print("Usage: save <file.json>")
            return
        data = self.bc.to_dict()
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved to {path}")
        except OSError as e:
            print(f"Failed to save: {e}")

    def do_load(self, path=None):
        if not path:
            print("Usage: load <file.json>")
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.bc = self.bc.from_dict(data)
            self.current_user = None
            print(f"Loaded from {path}. You are logged out.")
        except (OSError, json.JSONDecodeError) as e:
            print(f"Failed to load: {e}")

    def do_exit(self):
        raise SystemExit

    def do_quit(self):
        raise SystemExit
