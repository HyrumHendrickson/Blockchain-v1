# Kids Blockchain Demo

A simple, self-contained Python project that teaches the basics of blockchains using a friendly command-line shell.

## Features

- Interactive shell with `help`-driven commands
- Create users, login/logout, and list users
- Send coins between users (pending transactions)
- Mine a block to confirm pending transactions
- Mining reward paid to the miner (current logged-in user)
- Inspect balances, pending transactions, and the full chain
- Save and load state from disk

## Quick Start

Requires Python 3.9+ (standard library only).

```bash
# 1) Extract the zip
unzip kids_blockchain_demo.zip
cd kids_blockchain_demo

# 2) Run
python main.py
```

> No third-party packages required. The app runs its own interactive shell "env" inside your terminal.

## Example Session

```
> help
> create_user alice
> create_user bob
> login alice
> faucet 50              # Give yourself some starter coins from the system
> send bob 10 for lunch  # Create a pending transaction
> pending                # See it in the mempool
> mine                   # Confirm pending transactions in a new block
> balance                # Check balances
> chain                  # Inspect the blockchain
> logout
> login bob
> balance
> save demo.json
> exit
```

## Design Overview

- **Account model:** Balances are computed by scanning confirmed (on-chain) and pending transactions.
- **Blocks:** Each block contains a list of transactions, a previous hash, a timestamp, a nonce, and its own hash.
- **Mining:** Proof-of-work with an adjustable difficulty (default: 2 leading zeroes). A mining reward is granted to the miner.
- **Persistence:** Use `save` and `load` to persist or resume a session.

## Commands

- `help` — Show available commands
- `create_user <name>`
- `users`
- `login <name>`
- `logout`
- `whoami`
- `faucet <amount>` — Mint from the SYSTEM account to yourself (teaching aid)
- `send <to> <amount> [note...]`
- `pending`
- `mine`
- `difficulty [N]` — Get or set difficulty
- `reward [AMOUNT]` — Get or set mining reward
- `balance [name]` — Default: current user
- `chain [n]` — Show last `n` blocks or full chain
- `save <filepath.json>`
- `load <filepath.json>`
- `exit` / `quit`

## Safety Notes

- This is a learning tool, not a real cryptocurrency.
- There is no networking; everything runs locally in one process.
