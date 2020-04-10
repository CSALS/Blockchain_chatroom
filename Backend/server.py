import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from flask_cors import CORS
from urllib.parse import urlparse
from blockchain import Blockchain

app = Flask(__name__)
cors = CORS(app)

blockchain = Blockchain()

node_address = str(uuid4()).replace('-', '')

print(node_address)

@app.route('/login', methods=['POST'])
def login_func():
    username = request.json['username']
    passwd = request.json['password']
    print(username, passwd)
    return jsonify({'username': username, 'password':passwd}), 200

@app.route('/signup', methods=['POST'])
def signup_func():
    name = request.json['name']
    username = request.json['username']
    passwd = request.json['password']
    print(name, passwd)
    return jsonify({'name': name, 'username':username, 'password':passwd}), 200

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_data(sender = node_address, msg = "Hello World")
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'data': block['data']}
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if the Blockchain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

# Adding new data to the Blockchain
@app.route('/add_data', methods = ['POST'])
def add_data():
    json = request.get_json()
    data_keys = ['sender','msg']
    if not all(key in json for key in data_keys):
        return 'Some elements of the data are missing', 400
    index = blockchain.add_data(json['sender'], json['amount'])
    response = {'message': f'This data will be added to Block {index}'}
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain

# Connecting new nodes
@app.route('/connect_node', methods = ['POST'])
def connect_node():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return "No node", 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All the nodes are now connected. The Blockchain now contains the following nodes:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest chain if needed
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 5000)