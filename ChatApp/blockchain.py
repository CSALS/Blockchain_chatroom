import datetime
import hashlib
import json
from urllib.parse import urlparse
import requests
import random
import pickle

class Blockchain:

    def __init__(self):
        '''
        chain: a list of blocks.
        data: temporary storage of data, yet to be mined
        storage: used for verification of a transaction.
        nodes: set of nodes through which the blockchain is distributed

        This constructor creates a genesis block, and connects the current
        node with all other nodes.
        '''
        self.chain = []
        self.data = ""
        self.createBlock(nonce = 1, previous_hash = '0')
        self.nodes = set()
        self.storage = {'sender':'',
                        'msg':'',
                        'h':'',
                        's':''}

        with open("nodes.json") as f:
            for node in json.load(f)['nodes']:
                self.add_node(node)
        print("connected nodes: ", self.nodes)

        try:
            with open('database', 'rb') as db:
                self.chain = pickle.load(db)
        except EOFError:
            pass
        print(self.chain)
    
    def createBlock(self, nonce, previous_hash):
        '''
        nonce: an integer value
        previous_hash: hash value of the previous block
        returns: a block.

        This function constructs a block. The block contains
        index: block number in the chain,
        timestamp: time at which the block is created,
        nonce: an integer value used for proof of work,
        previous_hash: hash value of the previous block,
        data: set of transactions (messages)
        '''
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'nonce': nonce,
                 'previous_hash': previous_hash,
                 'data': self.data}
        self.data = []
        self.chain.append(block)
        if nonce != 1 and previous_hash != '0':
            with open('database', 'wb') as db:
                pickle.dump(self.chain, db)
        return block

    def get_previous_block(self):
        '''
        This method returns the last block in the blockchain.
        '''
        return self.chain[-1]

    def proof_of_work(self, previous_nonce):
        '''
        previous_nonce: nonce value used previously,

        This function implements the proof of work in blockchain.
        For each nonce value, hash of new_nonce^2 - previous_nonce^2 is calculated using sha256,
        if the hex value has '0000' in its beginning, then the new_nonce is accepted
        and it is returned
        '''
        new_nonce = 1
        check_nonce = False
        while check_nonce is False:
            hash_operation = hashlib.sha256(str(new_nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_nonce = True
            else:
                new_nonce += 1
        return new_nonce
    
    def hash(self, block):
        '''
        This function takes a block as input and returns its hash value
        calculated using sha256 algorithm.
        '''
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        '''
        This function takes a blockchain as input and check if
        the previous hash values in the blocks are correct. It also
        checks if the nonce values are valid or not.
        '''
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_nonce = previous_block['nonce']
            nonce = block['nonce']
            hash_operation = hashlib.sha256(str(nonce**2 - previous_nonce**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True
    
    def add_data(self, sender='', msg='', param='', param_type=''):
        '''
        sender: username of the message sender
        msg: content of the message
        param: h/s depending on param_type
        param_type: h/s/r

        This function is used in multiple ways depending on param type
        when mining a block it returns -1 or -2
        1) when the user sends h, it returns a random bit b.
        2) when the user sends r, it returns the result of verification of transaction only. 
        This is used for the user to do ZKP multiple times before finally adding message.
        3) when the user sends s, it verifies the transaction
        using public key of the user and the method 'verifyTransaction'.
        if the transaction is verified, it adds the transaction(msg) to data variable
        and returns the new index.
        '''
        if msg == 'mining_block':
            if len(self.data) == 0: return -1
            else: return -2

        if param_type == 'h':
            self.storage['sender'] = sender
            self.storage['msg'] = msg
            self.storage['h'] = param
            self.storage['b'] = random.randint(0, 1)
            return self.storage['b']

        elif param_type == 'r':
            self.storage['s'] = param
            keys = self.get_publickeys(self.storage['sender'])
            verify_res = self.verifyTransaction(keys["A"], keys["B"], keys["p"])
            print("verify ", verify_res)
            return verify_res

        elif param_type == 's':
            self.storage['s'] = param
            keys = self.get_publickeys(self.storage['sender'])
            if self.verifyTransaction(keys["A"], keys["B"], keys["p"]):
                self.data.append({'sender': self.storage['sender'],
                                    'time': str(datetime.datetime.now()),
                                    'msg': self.storage['msg']})
                previous_block = self.get_previous_block()
                return previous_block['index'] + 1

        return -99
    
    def add_node(self, address):
        '''
        This function takes address of a node and adds
        it to the set of nodes in the distributed system.
        '''
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    def replace_chain(self):
        '''
        This function updates the current blockchain with
        the longest blockchain among all nodes. 
        '''
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            try:
                response = requests.get(f'http://{node}/get_chain')
                if response.status_code == 200:
                    length = response.json()['length']
                    chain = response.json()['chain']
                    if length > max_length and self.is_chain_valid(chain):
                        max_length = length
                        longest_chain = chain
            except:
                pass
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

    def get_publickeys(self, user):
        '''
        This function returns the public keys of a user.
        '''
        with open('publickeys.json') as f:
            keys = json.load(f)
        return keys.get(user)

    def verifyTransaction(self, A, B, p):
        '''
        This function verifies a transaction using 
        public key of a user (A, B, p) using discrete log math.

        A: generator
        B: (A^x)(mod p)
        p: large prime number
        
        - The user sends h = (A^r)(mod p) where r is a random number
        generated by the user. 
        - the verifier sends a random bit b
        - the user sends s = (r+bx)(mod (p-1))
        - This function computes (A^s)(mod p) and h(B^b)(mod p).
        If these two values are equal, the transaction is considered
        to be verified, else not.

        The user sends h, s using the endpoint /add_data and
        the verifier sends b using the method add_data() in blockchain class.
        '''
        s = self.storage['s']
        h = self.storage['h']
        b = self.storage['b']

        tmp1 = (A**s)%p
        tmp2 = (h*(B**b))%p
        if tmp1 == tmp2:
            return True
        else:
            return False