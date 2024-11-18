from flask import Flask, render_template, request, redirect, url_for, flash, Response
from flask_sqlalchemy import SQLAlchemy
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, Payment, PaymentWay, InquiryKind
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)

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

# def calculate_password_hash(password):
#     text = password.encode('utf-8')
#     result = hashlib.sha512(text).hexdigest()
#     return result

# ---- Welcomeページ ----
@app.route('/', methods=['GET', 'POST'])
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

        # passwordのハッシュ化
        hashdPassword = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(userName=userName, displayName=displayName, mailAddress=mailAddress, password=hashdPassword) 

        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
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
        user = User.query.filter(User.userName==userName).first()
        if user:
            if user and bcrypt.check_password_hash(user.password, password):  # userがNoneでないかも確認
                print("成功")
                login_user(user)
                return redirect('/top')
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
    return redirect('/login')

@app.route('/top')
@login_required
def top():
    return render_template('top.html')


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.run(debug=True)