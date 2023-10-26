from datetime import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        """
        Insere na chain um novo bloco
        """

        # O bloco fica como um dicionário
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions': self.transactions}
        # O próximo bloco deve iniciar com uma lista de transactions limpa
        self.transactions = []
        self.chain.append(block)
        return block

    def get_previous_block(self):
        return self.chain[-1]

    def proof_of_work(self, previous_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # Gera um novo hash e retorna em hexadecimal
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            # Isso ajusta a dificuldade da mineração
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        """
        Recebe um bloco e retorna o hash deste bloco
        """
        # Gera o Json do bloco e transforma em um array de bytes
        encoded_block = json.dumps(block, sort_keys = True).encode()
        # Gera um hash a partir destes bytes e retorna em hexadecimal
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        """
        Verifica se cada bloco tem um proof of word válido
        refazendo a verificação de hash de um bloco com seu
        anterior
        """
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            # Isso é o que garante a corrente, a verificação do hash dos blocos
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            # O atributo proof do bloco é válido?
            previous_proof = previous_block['proof']
            proof = block['proof']
            # Refaz a operação do proof of work
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            # Checa o próximo bloco
            previous_block = block
            block_index += 1
        return True

    def addTransaction(self, sender, receiver, amount):
        transaction = {
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        }
        self.transactions.append(transaction)
        previous_block_list = self.get_previous_block()
        return previous_block_list['index'] + 1

app = Flask(__name__)


blockchain = Blockchain()

# Faz a mineração do bloco
@app.route('/mine_block', methods = ['GET'])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message': 'Parabens voce acabou de minerar um bloco!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    return jsonify(response), 200

# Retorna todo o blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {'message' : ' Tudo certo, o blockchain e valido '}
    else:
        response = {'message' : ' O blockchain nao e valido '}
    return jsonify(response), 200

app.run(host = '0.0.0.0', port = 5000)
