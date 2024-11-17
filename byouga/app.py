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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/add_user_template')
def add_user_template():
    data = User.query.all()
    return render_template('add_user_template.html', data=data)

@app.route('/add_user', methods=['POST'])
def add_user():
    userName = request.form.get('userName')
    displayName = request.form.get('displayName')
    mailAddress = request.form.get('mailAddress')
    password = request.form.get('password')

    new_user = User(userName=userName, displayName=displayName, mailAddress=mailAddress, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/save-image', methods=['POST'])
def save_image():
    data = request.get_json()
    image_data = data.get('image')

    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400

    image_bytes = decode_image(image_data)
    if not image_bytes:
        return jsonify({'error': 'Invalid image data'}), 400

    file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])

    new_image = Sale(filePath=file_path)
    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Image saved successfully', 'file_path': file_path}), 200

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(debug=True)
