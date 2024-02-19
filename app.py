from flask import Flask, g, render_template, request
import sqlite_utils
import os 
import toml 

app = Flask(__name__)

DATABASE = 'marketplace_data.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite_utils.Database(DATABASE)
    return db

def initialize_database():
    # Since SQLite has no ALTER TABLE support, 
    # check for table existence before creation
    db = get_db()
    if "buyers" not in db.table_names():
        db["buyers"].create({
            "name": str,
            "budget": float
        }, pk="name")  

    if "sellers" not in db.table_names():
        db["sellers"].create({
            "group_name": str,
            "balance": float
        }, pk="group_name") 

    if "products" not in db.table_names():
        db["products"].create({
            "id": int,
            "seller_group": str,
            "stock_level": int,
        }, pk="id", foreign_keys=[("seller_group", "sellers", "group_name")])


def load_seller_data(group_folder, toml_filename='store_data.toml'):
    file_path = os.path.join(group_folder, toml_filename)
    with open(file_path, 'r') as f:
        toml_data = toml.load(f)
    return toml_data['seller'] 


@app.route('/')
def marketplace():
    db = get_db()  # Get a database connection for this request
    products = db["products"].rows 
    return render_template('index.html', products=products) 

SELLER_DATA_PATH = 'seller_data.toml'  # Adjust the path if needed

def load_products_from_toml(toml_file):
    with open(toml_file, 'r') as f:
        data = toml.load(f)
    return data['seller'].get('products', []) 

@app.route('/buyer')
def buyer_page():
    buyer_name = 'buyer1' 
    products = load_products_from_toml(SELLER_DATA_PATH)

    db = get_db()
    try:
        buyer_balance = db["buyers"].get(buyer_name)['budget']
    except sqlite_utils.db.NotFoundError:
        # Handle cases where the buyer may not exist yet
        buyer_balance = 0.0

    # Update stock levels using placeholder logic - you'd have more precise queries here
    for product in products:
        product_id = product.get('id')  # Assumes you add an 'id' key to your TOML products 
        if product_id:
            try:
                 stock_level = db["products"].get(product_id)['stock_level']
                 product['stock_level'] = stock_level
            except sqlite_utils.db.NotFoundError:
                 pass  # Product might not be found - handle as needed

    return render_template('buyer.html', buyer_name=buyer_name, products=products, buyer_balance=buyer_balance)

if __name__ == '__main__':
    initialize_database() 
    app.run(debug=True) 