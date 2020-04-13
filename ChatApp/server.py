import datetime
import hashlib
import json
from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import requests
from uuid import uuid4
from flask_cors import CORS
from urllib.parse import urlparse
from blockchain import Blockchain
from login import verify_login
from keygen import *
import os

app = Flask(__name__)
cors = CORS(app)

blockchain = Blockchain()

node_address = str(uuid4()).replace('-', '')

print(node_address)

# Webpages Begin
# port = 5000
port = os.path.basename(os.getcwd())[-4: ]
BASE_URL = f"http://localhost:{port}"

logged_in = 0 # Used to prevent anyone not logged in from accessing chatroom page
@app.route('/', methods=['GET', 'POST'])
def home():
    global logged_in
    share_keys()
    error = None
    if request.method == 'POST':
        # correct = verify_login(request.form['username'], request.form['password'])
        correct = True
        if not correct:
            error = 'Invalid Credentials'
        else:
            logged_in = logged_in + 1
            api_url = BASE_URL + "/add_user"
            payload = json.dumps({"username": request.form['username'], "password": request.form["password"]})
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", api_url, headers=headers, data = payload)

            return redirect(url_for('chatroom', username=request.form['username']))
    return render_template('login.html', error=error)

@app.route('/chatroom/<username>', methods=['GET', 'POST'])
def chatroom(username):
    global logged_in
    if request.method == 'GET' and logged_in != 0:
        return render_template('chatroom.html', username=username)
    else:
        return redirect('/')


@app.route('/logout', methods=['GET'])
def logout():
    print("logging out")
    global logged_in
    print(logged_in)
    logged_in = logged_in - 1
    print(logged_in)
    return render_template('login.html', error=None)
# Webpages End

def share_keys():
    for node in blockchain.nodes:
        api_url = f'http://{node}/update_publickeys'
        keys = {}
        with open('publickeys.json') as f:
            try:
                keys = json.load(f)  
            except:
                pass
        payload = json.dumps({"publickeys": keys})
        headers = {
            'Content-Type': 'application/json'
        }
        try:
            response = requests.request("POST", api_url, headers=headers, data = payload)
            with open('publickeys.json','w') as f:
                json.dump(response.json()["keys"], f)
        except:
            pass

@app.route('/add_user', methods=['POST'])
def add_user():
    share_keys()

    json_req = request.get_json()
    keys = {}
    with open('publickeys.json') as f:
        try:
            keys = json.load(f)  
        except:
            pass

    if json_req["username"] in keys:
        return jsonify({"Message": "username already exists", "keys": json_req["username"]}), 200

    k = keygen(json_req["password"])
    keys[json_req["username"]] = {"A": k['A'], "B": k['B'], "p":k['p']}

    with open('publickeys.json','w') as f:
        json.dump(keys, f)

    return jsonify({"Message": "New User added to keystore"}), 200

# Mining a new block
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_nonce = previous_block['nonce']
    nonce = blockchain.proof_of_work(previous_nonce)
    previous_hash = blockchain.hash(previous_block)
    print("data queue: ", blockchain.data)
    tmp = blockchain.add_data(sender = node_address, msg = "mining_block")

    if tmp == -1:
        response = {"message": "There are no messages to mine a new block!"}
    else:
        block = blockchain.createBlock(nonce, previous_hash)
        response = {'message': 'Congratulations, you just mined a block!',
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'nonce': block['nonce'],
                    'previous_hash': block['previous_hash'],
                    'data': block['data']}

        with open('database', 'wb') as file:
            pickle.dump(blockchain.chain, file)
    return jsonify(response), 200

# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain),
                'unmined_msgs': blockchain.data}
    return jsonify(response), 200


@app.route('/view_user', methods = ['GET'])
def viewUser():
    username = request.args["name"]
    response = {'messages':[]}
    for block in blockchain.chain:
        if len(block['data'])>0:
            for d in block['data']:
                if d['sender'] == username:
                    response['messages'].append(d)


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
    if 's' in json:
        index = blockchain.add_data(param=json['s'], param_type='s')
        response = {'message': f'This data will be added to Block {index}'}
    else:
        data_keys = ['sender','msg', 'h']
        if not all(key in json for key in data_keys):
            return 'Some elements of the data are missing', 400
        b = blockchain.add_data(json['sender'], json['msg'], json['h'], 'h')
        response = {"b": b}

    return jsonify(response), 200

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

@app.route('/get_publickeys', methods = ['POST'])
def get_public_keys():
    json_req = request.get_json()
    print(json_req, " in get_public_keys")
    username = json_req["username"]
    keys = {}
    with open('publickeys.json') as f:
        try:
            keys = json.load(f)  
        except:
            pass
    if username in keys:
        print("found keys for ",username, " ", keys[username])
        return jsonify({"keys": keys[username]}), 200
    
    return jsonify({"keys":""}), 200

@app.route('/update_publickeys', methods = ['POST'])
def update_publickeys():
    json_req = request.get_json()
    new_keys = json_req["publickeys"]
    keys = {}
    with open('publickeys.json') as f:
        try:
            keys = json.load(f)  
        except:
            pass

    for k in list(new_keys.keys()):
        if k not in keys:
            keys[k] = new_keys[k]
    
    with open('publickeys.json','w') as f:
        json.dump(keys, f)

    return jsonify({"keys":keys}), 200



# Running the app
app.run(host = '0.0.0.0', port = port)