from flask import Flask, session, render_template, request, redirect, url_for, flash, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, Payment, PaymentWay, InquiryKind
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from datetime import date, datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sample.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) # 複数ユーザーが各々のページにアクセスできる

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

@app.route('/top')
@login_required
def top():
    return render_template('top.html')

# ---- Mypage ----
@app.route('/myPage')
@login_required
def myPage():
    userId = session.get('userId')
    user = User.query.get(userId)
    return render_template('myPage.html', user=user)


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        app.run(debug=True)