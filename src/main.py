
import json
import os
import sys
from datetime import datetime
from kids_blockchain.shell import BlockchainShell

def main():
    print("Kids Blockchain Demo")
    print("Type 'help' to see available commands.")
    shell = BlockchainShell()
    shell.cmdloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")
        sys.exit(0)
