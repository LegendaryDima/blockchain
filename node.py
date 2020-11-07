from blockchain import Blockchain
from uuid import uuid4
from verification import Verification

class Node:

    def __init__(self):
        self.id = str(uuid4())
        self.blockchain = Blockchain(self.id)

    def get_transaction_value(self):
        tx_recipient = input('Enter the recipient of the transaction: ')
        tx_amount =  float(input('Your transaction amount please: '))
        return tx_recipient, tx_amount

    def get_user_choice(self):
        return input('Your choice: ')

    def print_blockchain_elements(self):
        for block in self.blockchain.blockchain:
            print('Outputting Block')
            print(block)

        else:
            print('-' *  20)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print('4: Check transaction validity')
            print('q: Quit')
            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.get_open_transactions())
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print('There are invalid transactions')
            # elif user_choice == 'h':
            #     if len(blockchain) >= 1:
            #         blockchain[0] = {
            #         'previous_hash': hashed_block, 
            #         'index': len(blockchain), 
            #         'transactions': [{'sender': 'Chris', 'recipient': 'Max', 'amount': 100.0}]
            #         }
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                raise(ValueError('Input was invalid, please pick a value from the list!'))

            print('Choice registered!')
            if not Verification.verify_chain(self.blockchain.blockchain):
                self.print_blockchain_elements()
                print('Invalid blockchain')
                break
            print(self.blockchain.get_balance())
        print('Done!')

node = Node()
node.blockchain.load_data()
node.listen_for_input()