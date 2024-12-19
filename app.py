# MARK:インポート
from flask import Flask, render_template, request, redirect, url_for, flash, Response, make_response, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, Payment, PaymentWay, InquiryKind
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_bcrypt import Bcrypt
from datetime import date, datetime
from sqlalchemy.orm import joinedload, Session
import os
import base64

# MARK:インスタンス化
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

# MARK:ログイン情報保持
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

#　MARK: Welcomeページ 
@app.route('/', methods=['GET', 'POST'])
@logout_required
def index():      
    if request.method == 'GET':
        user = User.query.all()
        return render_template('index.html', user = user)
    
# MARK: saleDetail
@app.route('/saleDetail/<int:sale_id>', methods=['GET', 'POST'])
def saleDetail(sale_id):
    # 商品情報をデータベースから取得
    sale = Sale.query.get(sale_id)
    bids = Bid.query.filter_by(saleId=sale_id).all()
    currentPrice = db.session.query(Bid.bidPrice).filter_by(saleId=sale_id).order_by(Bid.bidPrice.desc()).first()
    currentPrice = currentPrice[0] if currentPrice else sale.startingPrice

    if sale is None:
        # 商品が見つからない場合の処理
        return "商品が見つかりません", 404
    
    # 商品情報をテンプレートに渡す
    if sale is None:
        flash('Sale not found', 'error')
        return redirect(url_for('top'))
    return render_template('saleDetail.html', sale=sale, bids=bids, currentPrice=currentPrice)

    
# MARK: 入札
@app.route('/bid', methods=['POST'])
@login_required
def bid():
    data = request.get_json()
    userId = session.get('userId')
    sale_id = data.get('saleId')
    amount = data.get('amount')
    
    # saleテーブルのcurrentPriceを更新
    sale = Sale.query.filter_by(saleId=sale_id).first()
    sale.currentPrice = amount
    
    print(f"user_id:{userId}, sale_id: {sale_id}, amount: {amount}")

    # Bidテーブルに新しい入札を追加
    new_bid = Bid(userId=userId, saleId=sale_id, bidPrice=amount)
    
    db.session.add(new_bid)
    db.session.commit()

    return jsonify({'success': True, 'message': '入札が成功しました'})

# MARK: サインアップページ
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


# MARK: ログインページ
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

# MARK: ログアウト
@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('userId') # ログアウト時にsessionからユーザーIDを削除
    print("ログアウト完了")
    return redirect('/login')

# MARK: トップページ
@app.route('/top')
@login_required
def top():
    userId = session.get('userId') # 利用しているuserIdの取得
    print("userIdです！", userId)
    sales = Sale.query.all()  # すべての商品を取得
    
    liked_sales = (
        db.session.query(Like.saleId)
        .filter_by(userId=userId)
        .all()
    )  # ユーザーが過去に「いいね」をした商品IDのリストを取得
    liked_sale_ids = [sale[0] for sale in liked_sales]  # 取得したsale_idをリスト化
    sales=db.session.query(Sale).all()        
    return render_template('top.html', sales=sales, userId=userId, liked_sale_ids=liked_sale_ids)

# MARK: いいね情報受け取りroute
@app.route('/like', methods=['POST'])
def like_sale():
    user_id = request.form['userId']
    sale_id = request.form['saleId']
    
    # すでにこのユーザーがこの商品に「いいね」をしていないか確認
    existing_like = Like.query.filter_by(saleId=sale_id, userId=user_id).first()
    
    if existing_like:
        # すでに「いいね」している場合は削除
        db.session.delete(existing_like)
        db.session.commit()
        action = 'removed'
    else:
        # 新たに「いいね」を追加
        new_like = Like(userId=user_id, saleId=sale_id)
        db.session.add(new_like)
        db.session.commit()
        action = 'added'
    
    # 「いいね」された商品に対する「いいね」の数を取得
    like_count = Like.query.filter_by(saleId=sale_id).count()
    print(f"Like count for sale {sale_id}: {like_count}")
    return jsonify({'action': action, 'likeCount': like_count})

# MARK: いいね一覧ページ
@app.route('/myLikeList')
@login_required
def myLikeList():
    userId = session.get('userId')
    user = User.query.get(userId) # userIdからそのユーザー情報を取得
    myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Like.likeId.desc()).all()
    print(myLikeList)
    return render_template('myLikeList.html', user=user, myLikeList=myLikeList)

# MARK: 並び順を渡すurl
@app.route('/sort_products')
def sort_products():
    userId = session.get('userId')
    sort_order = request.args.get('order', 'likeOrder')  # デフォルト値としてprice_ascを設定
    print("並び替え：",sort_order)

    # 並び替えの条件を動的に変更
    if sort_order == 'likedOrder':
        # いいねした順
        myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Like.likeId.desc()).all()
    elif sort_order == 'orderCheapPrice':
        # 価格の安い順
        myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Sale.startingPrice.asc()).all()
    elif sort_order == 'orderHighPrice':
        # 価格の高い順
        myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Sale.startingPrice.desc()).all()

    # 商品情報を辞書形式に整形
        # saleファイルパスを正しいURL形式に変換
    for sale in myLikeList:
        sale.filePath = url_for('static', filename=sale.filePath)

    product_list = [{'id': sale.saleId, 'title': sale.title, 'startingPrice': sale.startingPrice, 'filePath': sale.filePath} for sale in myLikeList]
    # 結果をJSON形式で返す
    return jsonify(product_list)

# MARK: マイページ
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


# MARK: canvas→画像変換
def decode_image(image_data):
    try:
        image_data = image_data.split(",")[1]
        return base64.b64decode(image_data)
    except (IndexError, base64.binascii.Error):
        return None

# MARK: 画像保存
def save_image_to_file(image_bytes, upload_folder):
    file_name = f"image_{len(os.listdir(upload_folder)) + 1}.png"
    file_path = os.path.join(upload_folder, file_name).replace('\\', '/')
    with open(file_path, 'wb') as f:
        f.write(image_bytes)
    return file_path

# MARK:　出品ページ
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

    userId = session.get('userId') # 今使っているユーザーのuserIdの取得
    user = User.query.get(userId) # userIdからuser情報受け取り
    displayName = user.displayName # displayNameの取得

    new_sale = Sale(userId=userId, displayName=displayName, title=title, filePath=file_path, startingPrice=price,currentPrice=price, creationTime=time)
    new_bid = Bid(userId=userId, saleId=new_sale.saleId, bidPrice=price)
    db.session.add(new_sale, new_bid)
    db.session.commit()

    return jsonify({'message': 'Sale added successfully'}), 201

# MARK: 描画ページ
@app.route('/draw')
def draw():
    return render_template('draw.html')

# MARK: 出品ページ処理
@app.route('/result')
def result():
    return render_template('result.html')

# ---- ユーザーデータの仮挿入 ----
# def add_user():
#     dummy_users = [
#         User(userName='user1', displayName='User One', mailAddress='user1@example.com', password='password1'),
#         User(userName='user2', displayName='User Two', mailAddress='user2@example.com', password='password2'),
#         User(userName='user3', displayName='User Three', mailAddress='user3@example.com', password='password3')
#     ]
#     db.session.bulk_save_objects(dummy_users)
#     db.session.commit()

# MARK: テーブルの作成
if __name__ == '__main__': 
    with app.app_context():
        # db.drop_all() # テーブルの全削除
        db.create_all()
        # add_user() # userデータの仮挿入
    app.run(debug=True)