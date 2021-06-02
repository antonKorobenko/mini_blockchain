from hashlib import sha256
from datetime import datetime
import json

class Transaction:
    def __init__(self, from_address, amount, to_address):
        self.fromAddress = from_address
        self.amount = amount
        self.toAddress = to_address

    def toString(self):
        return "{} {} {} ".format(str(self.fromAddress), str(self.amount), str(self.toAddress))

    def toDict(self):
        obj = {
            "fromAddress": self.fromAddress,
            "amount": self.amount,
            "toAddress": self.toAddress
        }
        return obj


class Block:
    def __init__(self, index, timestamp, transactions, previous_hash=" "):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = 0
        self.hash = self.calculateHash()

    def calculateHash(self):
        return str(sha256((str(self.index) + str(self.timestamp) + str(self.transactionsToString()) + str(self.nonce) + str(self.previous_hash)).encode('utf-8')).hexdigest())

    def transactionsToString(self):
        res = ""
        for i in self.transactions:
            res = res + i.toString()
        return res

    def mineBlock(self, difficulty):
        while not self.hash.startswith("0" * difficulty):
            self.nonce += 1
            self.hash = self.calculateHash()
        print("Block {} was mined: {} for nonce = {}\n".format(self.index, self.hash, self.nonce))

    def toDict(self):
        obj = {
            "index": self.index,
            "transactions": [i.toDict() for i in self.transactions],
            "timestamp": str(self.timestamp),
            "previous hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": str(self.hash)
        }
        return obj


class Blockchain:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.chain = [self.createGenesisBlock()]


    def createGenesisBlock(self):
        b = Block(0, "2021-01-01 00:00:00", [Transaction("root", 100, "A"), Transaction("root", 10, "B")], "0")
        b.mineBlock(self.difficulty)
        return b

    def addBlock(self):
        n = int(input("Enter number of transactions\n"))
        transactions = []
        for i in range(n):
            f_a = str(input("Enter from_Address\n"))
            am = int(input("Enter amount\n"))
            t_a = str(input("Enter to_Address\n"))
            transactions.append(Transaction(f_a, am, t_a))
        b = Block(len(self.chain), datetime.now(), transactions, self.getLastBlock().hash)
        print("Mining new block\n")
        b.mineBlock(self.difficulty)
        self.chain.append(b)

    def isChainValid(self):
        realGenesisBlock_hash = self.createGenesisBlock().calculateHash()
        if realGenesisBlock_hash != self.chain[0].calculateHash():
            print("Chain is invalid in genesis block\n")
            return False

        for i in range(1, len(self.chain)):
            currentBlock = self.chain[i]

            for j in range(len(self.chain[i].transactions)):
                if not self.isTransactionValid(self.chain[i].transactions[j]):
                    print("Chain is invalid in block {}, transaction {}\n".format(i, j))
                    return False

            if currentBlock.calculateHash() != currentBlock.hash:
                print("Chain is invalid in block {}\n".format(i))
                return False
        print("Chain is valid")
        return True

    def getLastBlock(self):
        return self.chain[len(self.chain) - 1]

    def isTransactionValid(self, transaction):
        if self.getBalanceOfAddress(transaction.fromAddress) < 0:
            return False
        return True

    def getBalanceOfAddress(self, address):
        balance = 0
        for block in self.chain:
            for trans in block.transactions:
                if trans.fromAddress == address:
                    balance -= int(trans.amount)
                if trans.toAddress == address:
                    balance += int(trans.amount)

        return balance

    def changeBlockByIndex(self):

        index = int(input("Enter index of block: "))
        work_block = self.chain[index]

        oper_type_1 = int(input("Enter typ3 of operation:\n1 - delete last transaction\n2 - change first transaction\n"))
        if oper_type_1 == 1:
            work_block.transactions.pop()
            work_block.hash = work_block.calculateHash()
        elif oper_type_1 == 2:
            oper_type_2 = int(input("Enter what you want to change: 1 - fromAddress, 2 - amount, 3 - toAddress\n"))
            if oper_type_2 == 1:
                new_fromAddress = input("Enter new fromAddress\n")
                work_block.transactions[0].from_address = new_fromAddress
                work_block.hash = work_block.calculateHash()
            elif oper_type_2 == 2:
                new_amount = input("Enter new input\n")
                work_block.transactions[0].amount = new_amount
                work_block.hash = work_block.calculateHash()
            elif oper_type_2 == 3:
                new_toAddress = input("Enter new toAddress\n")
                work_block.transactions[0].toAddress = new_toAddress
                work_block.hash = work_block.calculateHash()

        print("Mining changed block\n")
        work_block.mineBlock(self.difficulty)

    def writeToFile(self, filename):
        f = open(filename, 'w')
        obj = {
            "difficulty": self.difficulty,
            "chain": [i.toDict() for i in self.chain]
        }
        obj_json = json.dumps(obj, indent=4)
        f.write(obj_json)

    def printBlockChain(self):
        obj = {
            "difficulty": self.difficulty,
            "chain": [i.toDict() for i in self.chain]
        }
        obj_json = json.dumps(obj, indent=4)
        print(obj_json)

    def printBlocks(self):
        for i in self.chain:
            obj = i.toDict()
            print(json.dumps(obj, indent=4))
            print("\n")


if __name__ == "__main__":
    bc = Blockchain(3)
    while True:
        command = input("Enter 1 to add block\n2 to change block by index\n3 to get balance by address\n0 to exit\n")
        if command == "1":
            bc.addBlock()
            bc.printBlocks()
            bc.isChainValid()

        elif command == "2":
            bc.changeBlockByIndex()
            bc.printBlocks()
            bc.isChainValid()

        elif command == "3":
            address = str(input("Enter address\n"))
            print(f"Balance pf {address} is {bc.getBalanceOfAddress(address)}")

        elif command == "4":
            file = str(input("Enter filename\n"))
            bc.writeToFile(file)

        elif command == "0":
            break
