from functools import reduce
import hashlib as hl
from collections import OrderedDict
import json
import pickle

from block import Block
from hash_util import hash_block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10

class Blockchain:
    def __init__(self, hosting_node):
        genesis_block = Block(0, '', [], 100, 0)
        # Initializing our blockchain list
        self.blockchain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node

    @property
    def chain(self):
        return self.__blockchain[:]

    @chain.setter
    def chain(self, val):
        self.__blockchain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                file_content = f.readlines()
                
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.blockchain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(tx['sender'], tx['recipient'], tx['amount'])
                    updated_transactions.append(updated_transaction)
                    self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass
        finally:
            print('Cleanup')




    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.blockchain]]
                f.write(json.dumps(saveable_chain))
                f.write('\n')
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print('Saving failed!')

    def get_balance(self):
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.blockchain]
        open_tx_sender = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self. blockchain]
        amount_recieved = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        return amount_recieved - amount_sent


    def proof_of_work(self):
        last_block = self.blockchain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        counter = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
            counter += 1
        print(counter)
        return proof


    def get_last_bc_val(self):
        """ Returns the last value of the current blockchain"""
        if len(self.__blockchain) < 1:
            return None
        return self.__blockchain[-1]



    def add_transaction(self, recipient, sender, amount=1.0):
        #transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            # participants.add(sender)
            # participants.add(recipient)
            self.save_data()
            return True
        return False


    def mine_block(self):
        last_block = self.blockchain[-1]
        hashed_block = hash_block(last_block)
        proof = self.proof_of_work()
        # reward_transaction = {
        #     'sender': 'MINING', 
        #     'recipient': owner, 
        #     'amount': MINING_REWARD
        # }
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)
        copied_transactions = self.__open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(len(self.blockchain), hashed_block, copied_transactions, proof)
        self.blockchain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True