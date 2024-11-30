import os
import base64
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, Payment, PaymentWay, InquiryKind

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './static/upload_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

def decode_image(image_data):
    try:
        image_data = image_data.split(",")[1]
        return base64.b64decode(image_data)
    except (IndexError, base64.binascii.Error):
        return None

def save_image_to_file(image_bytes, upload_folder):
    file_name = f"image_{len(os.listdir(upload_folder)) + 1}.png"
    file_path = os.path.join(upload_folder, file_name)
    with open(file_path, 'wb') as f:
        f.write(image_bytes)
    return file_path

@app.route('/draw')
def draw():
    return render_template('draw.html')

@app.route('/result')
def result():
    return render_template('result.html')

# def add_user():
#     dummy_users = [
#         User(userName='user1', displayName='User One', mailAddress='user1@example.com', password='password1'),
#         User(userName='user2', displayName='User Two', mailAddress='user2@example.com', password='password2'),
#         User(userName='user3', displayName='User Three', mailAddress='user3@example.com', password='password3')
#     ]
#     db.session.bulk_save_objects(dummy_users)
#     db.session.commit()

@app.route('/add_sale', methods=['POST'])
def add_sale():
    data = request.get_json()
    image_data = data.get('image')
    time = data.get('time')
    price = data.get('price')
    title = data.get('title')

    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400

    image_bytes = decode_image(image_data)
    if not image_bytes:
        return jsonify({'error': 'Invalid image data'}), 400

    file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])

    new_sale = Sale(title=title, filePath=file_path, startingPrice=price, creationTime=time)
    db.session.add(new_sale)
    db.session.commit()

    return jsonify({'message': 'Sale added successfully'}), 201

if __name__ == '__main__': 
    with app.app_context():
        db.create_all()
        # db.drop_all() # テーブルの全削除
        # add_user() # userデータの仮挿入
    app.run(debug=True)