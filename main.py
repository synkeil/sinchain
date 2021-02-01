import json
import schedule
from timeloop import Timeloop
from datetime import timedelta
from uuid import uuid4

from flask import Flask, render_template, jsonify, request

from static.chain import Blockchain
from flask_cors import CORS, cross_origin
import time

import asyncio

tl = Timeloop()

app = Flask(__name__)

def job():
    print("doing a job")
    if len(blockchain.current_transactions) > 0:
        # We run the proof of work algorithm to get the next proof...
        last_block = blockchain.last_block
        last_proof = last_block['proof']
        proof = blockchain.proof_of_work(last_proof)

        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        blockchain.new_transaction({
            "sender": "0",
            "recipient": node_identifier,
            "amount": 1,
        })

        # Forge the new Block by adding it to the chain
        previous_hash = blockchain.hash(last_block)
        blockchain.new_block(proof, previous_hash)


@app.route('/')
def root():

    return render_template('index.html')

app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/foo": {"origins": "http://localhost:port"}})

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction({
        "sender": "0",
        "recipient": node_identifier,
        "amount": 1,
    })

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def new_transaction():
    values = request.get_json(force = True)

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient']
    print(values)
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values)

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

@tl.job(interval=timedelta(minutes=5))
def sample_job_every_2s():
    job()

if __name__ == '__main__':
        tl.start(block=False)
        app.run(host='0.0.0.0', port=8080, debug=True)