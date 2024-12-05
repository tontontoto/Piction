from flask import Flask, session, render_template, request, redirect, url_for, flash, Response, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, Payment, PaymentWay, InquiryKind
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from datetime import date, datetime
from sqlalchemy.orm import joinedload
import os
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) # 複数ユーザーが各々のページにアクセスできる
app.config['UPLOAD_FOLDER'] = './static/upload_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
bcrypt = Bcrypt()
#インスタンス化
login_manager = LoginManager()
#アプリをログイン機能を紐付ける
login_manager.init_app(app)

#現在のログインユーザーの情報を保持し、必要なときに参照できるようになる。
@login_manager.user_loader
def load_user(userId):
    return User.query.get(userId)

# ログインしているユーザに対してのアクセス制限をかけるデコレータ
def logout_required(f):
    def decorated_function(*args, **kwargs):
        # セッションにユーザーIDがある場合、リダイレクト
        if 'userId' in session:
            # ログイン後にアクセス可能ページにリダイレクト
            return redirect(url_for('top'))  
        return f(*args, **kwargs)
    return decorated_function




# ---- ユーザーデータの仮挿入 ----
# def add_user():
#     dummy_users = [
#         User(userName='user1', displayName='User One', mailAddress='user1@example.com', password='password1'),
#         User(userName='user2', displayName='User Two', mailAddress='user2@example.com', password='password2'),
#         User(userName='user3', displayName='User Three', mailAddress='user3@example.com', password='password3')
#     ]
#     db.session.bulk_save_objects(dummy_users)
#     db.session.commit()



# ---- Welcomeページ ----
@app.route('/', methods=['GET', 'POST'])
@logout_required
def index():      
    if request.method == 'GET':
        user = User.query.all()
        return render_template('index.html', user = user)


# ---- サインアップページ処理 ----
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        userName = request.form.get('userName')
        displayName = request.form.get('displayName')
        mailAddress = request.form.get('mailAddress')
        password = request.form.get('password')
        # privacyPolicy = request.form.get('privacyPolicy')

        # passwordのハッシュ化
        hashdPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(userName=userName, displayName=displayName, mailAddress=mailAddress, password=hashdPassword)

        db.session.add(new_user)
        db.session.commit()

        # ユーザーIDをセッションに保存　-> 後からIDから参照できるようになる
        session['userId'] = new_user.userId
        print(f'{userName}さんの登録が完了しました！')
        # sessionに保存 / 新規登録時ログインページ介さずTOPに遷移
        session['userId'] = new_user.userId
        login_user(new_user)
        print(session['userId'])
        return redirect('/top')
    else:
        return render_template('signup.html')


# ---- ログインページ処理 ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userName = request.form.get('userName')
        password = request.form.get('password')
        error = "ユーザーネームまたはパスワードが違います"
        # Userテーブルからusernameに一致するユーザを取得
        user = User.query.filter_by(userName=userName).first()
        if user:
            if user and bcrypt.check_password_hash(user.password, password):  # userがNoneでないかも確認
                print("成功")
                # sessionに保存
                session['userId'] = user.userId
                login_user(user)
                resp = redirect('/top')
                return resp
            else:
                # パスワードが違う時の処理
                return render_template('login.html', error=error)
        else:
            # ユーザーネームが違う時の処理
            return render_template('login.html', error=error)
    else:
        # method='GET'のとき
        return render_template('login.html')

# ---- ログアウト機能 ----
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('userId') # ログアウト時にsessionからユーザーIDを削除
    print("ログアウト完了")
    return redirect('/login')

# ---- toppage ----
@app.route('/top')
@login_required
def top():
    sales=db.session.query(Sale).all()        
    return render_template('top.html', sales=sales)

# ---- いいね情報受け取りroute ----


# ---- Mypage ----
@app.route('/myPage')
@login_required
def myPage():
    userId = session.get('userId')
    user = User.query.get(userId)

    # session(ログイン状態のuserId)のsaleの行を取り出し、
    # 外部キーのuserIdよりUserテーブルの中のデータを参照できる。
    sales = db.session.query(Sale).join(User).filter_by(userId=userId).all()
    for sale in sales:
        display_name = sale.user.displayName
        title = sale.title
        print(title)
        print(f"ユーザーの表示名: {display_name}")
    listing_number = db.session.query(Sale).filter(Sale.userId == userId).count()
            
    return render_template('myPage.html', user=user, sales=sales, listingNumber=listing_number)


# image_dataを受け取り、base64デコードして画像データを返す
def decode_image(image_data):
    try:
        image_data = image_data.split(",")[1]
        return base64.b64decode(image_data)
    except (IndexError, base64.binascii.Error):
        return None

# 画像データをファイルに保存し、ファイルパスを返す
def save_image_to_file(image_bytes, upload_folder):
    file_name = f"image_{len(os.listdir(upload_folder)) + 1}.png"
    file_path = os.path.join(upload_folder, file_name).replace('\\', '/')
    with open(file_path, 'wb') as f:
        f.write(image_bytes)
    return file_path

# ---- 出品ページ処理 ----
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
    file_path = file_path.replace(app.config['UPLOAD_FOLDER'], 'upload_images')

    new_sale = Sale(title=title, filePath=file_path, startingPrice=price, creationTime=time)
    db.session.add(new_sale)
    db.session.commit()

    return jsonify({'message': 'Sale added successfully'}), 201

# ---- 描画ページ ----
@app.route('/draw')
def draw():
    return render_template('draw.html')

# ---- 出品ページ処理 ----
@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__': 
    with app.app_context():
        db.drop_all() # テーブルの全削除
        db.create_all()
        
        # add_user() # userデータの仮挿入
    app.run(debug=True)