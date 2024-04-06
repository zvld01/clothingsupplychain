from flask import Flask, render_template, request, jsonify
import hashlib
import time
from typing import List, Dict
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256

app = Flask(__name__)

class Block:
    def __init__(self, index: int, transactions: List[Dict], timestamp: float, previous_hash: str):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.transactions}{self.timestamp}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

class Product:
    def __init__(self, product_id: str, details: str, status: str):
        self.product_id = product_id
        self.details = details
        self.status = status
        self.history = []

    def add_to_history(self, transaction):
        self.history.append(transaction)

class Blockchain:
    def __init__(self):
        self.chain = []
        self.pending_transactions = []
        self.products = {}
        self.create_genesis_block()
        self.private_key = RSA.generate(2048)
        self.public_key = self.private_key.publickey()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time.time(), "0")
        self.chain.append(genesis_block)

    def add_transaction(self, product_id: str, details: str, action: str, user: str):
        transaction = {
            "product_id": product_id,
            "details": details,
            "action": action,
            "user": user,
            "timestamp": time.time()
        }
        transaction_hash = SHA256.new(str(transaction).encode())
        signature = pkcs1_15.new(self.private_key).sign(transaction_hash)
        transaction['signature'] = signature.hex()

        if product_id not in self.products:
            self.products[product_id] = Product(product_id, details, action)
        else:
            self.products[product_id].status = action

        self.products[product_id].add_to_history(transaction)
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        if not self.pending_transactions:
            return False

        last_block = self.chain[-1]
        new_block = Block(len(self.chain), self.pending_transactions, time.time(), last_block.hash)
        self.chain.append(new_block)
        self.pending_transactions = []
        return True

    def get_product_history(self, product_id: str):
        if product_id in self.products:
            return self.products[product_id].history
        return None

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != prev_block.hash:
                return False
        return True

    def add_product(self, product_id: str, details: str):
        if product_id not in self.products:
            self.products[product_id] = Product(product_id, details, 'Produced')
            return True
        return False

    def delete_product(self, product_id: str):
        if product_id in self.products:
            del self.products[product_id]
            return True
        return False

    def view_inventory(self):
        return {product_id: {'details': product.details, 'status': product.status, 'signature': product.history[-1]['signature'] if product.history else 'N/A'} for product_id, product in self.products.items()}

blockchain = Blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_product', methods=['POST'])
def add_product():
    data = request.json
    product_id = data['product_id']
    product_type = data['product_type']
    price = {'tshirt': 40, 'pants': 60, 'shoes': 120}.get(product_type, 0)
    details = f"{product_type.capitalize()} - ${price}"
    blockchain.add_product(product_id, details)
    return jsonify({'message': 'Product added successfully'})

@app.route('/delete_product', methods=['POST'])
def delete_product():
    data = request.json
    product_id = data['product_id']
    if blockchain.delete_product(product_id):
        return jsonify({'message': 'Product deleted successfully'})
    return jsonify({'message': 'Product not found'}), 404

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    data = request.json
    product_id = data['product_id']
    action = data['action']
    user = data['user']

    if not all([product_id, action, user]):
        return jsonify({'message': 'All fields are required'}), 400

    if product_id not in blockchain.products:
        return jsonify({'message': 'Product not found'}), 404

    blockchain.add_transaction(product_id, blockchain.products[product_id].details, action, user)
    blockchain.mine_pending_transactions()
    return jsonify({'message': 'Transaction added and mined successfully'})

@app.route('/get_product_history', methods=['GET'])
def get_product_history():
    product_id = request.args.get('product_id')
    history = blockchain.get_product_history(product_id)
    return jsonify(history)

@app.route('/view_inventory', methods=['GET'])
def view_inventory():
    return jsonify(blockchain.view_inventory())

if __name__ == '__main__':
    app.run(debug=True)
