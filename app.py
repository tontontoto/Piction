from flask import Flask, session, render_template, request, redirect, url_for, flash, Response, make_response
from flask_sqlalchemy import SQLAlchemy
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, Payment, PaymentWay, InquiryKind
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from datetime import date, datetime
from sqlalchemy.orm import joinedload
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

# 仮データ
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

def add_sale():
    pass
    # userId = session.get('userId')
    # if userId:
    if True:
        sale1 = Sale(userId=1, title="テストの絵", filePass="upload_images/image_5.png", startingPrice="300")
        sale2 = Sale(userId=2, title="原宿の絵", filePass="upload_images/image_29.png", startingPrice="1000")
        sale3 = Sale(userId=1, title="落書き", filePass="upload_images/image_6.png", startingPrice="2000")
        sale4 = Sale(userId=1, title="くまさん", filePass="upload_images/image_22.png", startingPrice="2000")
        sale5 = Sale(userId=2, title="へたくそ日本地図", filePass="upload_images/image_7.png", startingPrice="2000")
        sale6 = Sale(userId=1, title="ももんが", filePass="upload_images/image_8.png", startingPrice="2000")
        sale7 = Sale(userId=1, title="HACHIWARE", filePass="upload_images/image_9.png", startingPrice="2000")
        # sale8 = Sale(userId=1, title="ももんが", filePass="upload_images/image_8.png", startingPrice="2000")
        # sale9 = Sale(userId=1, title="ももんが", filePass="upload_images/image_8.png", startingPrice="2000")
        # sale10 = Sale(userId=1, title="ももんが", filePass="upload_images/image_8.png", startingPrice="2000")
        # sale11 = Sale(userId=1, title="ももんが", filePass="upload_images/image_8.png", startingPrice="2000")

    db.session.add(sale1)
    db.session.add(sale2)
    db.session.add(sale3)
    db.session.add(sale4)
    db.session.add(sale5)
    db.session.add(sale6)
    db.session.add(sale7)
    db.session.commit()
    print(f"新しいSaleが登録されました。userId: {1}")

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        # # add_user()
        add_sale()
        app.run(debug=True)