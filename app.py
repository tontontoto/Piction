# MARK:インポート
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from model_sample import db, User, Sale, Category, Bid, Like, DB_URL, Inquiry
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from sqlalchemy import func
from azure.storage.blob import BlobServiceClient
from werkzeug.utils import secure_filename
import random
import string
import os
import base64

S_URL = os.environ.get("S_URL")
S_KEY = os.environ.get("S_KEY")
S_CNT = os.environ.get("S_CNT")
SAS = os.environ.get("SAS")

# MARK:インスタンス化
app = Flask(__name__)
#データベースのURLを設定
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) # 複数ユーザーが各々のページにアクセスできる

# # MARK: Azure Blob Storage設定
AZURE_CONNECTION_STRING = S_URL
AZURE_CONTAINER_NAME = S_CNT
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

print("データベースURL=" + DB_URL)
print("BLOB接続文字列=" + S_URL)

# ローカル画像保存先フォルダ
app.config['UPLOAD_FOLDER'] = './static/upload_images'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

try:
    db.init_app(app)
except Exception as e:
    print(e)
    
bcrypt = Bcrypt()
#インスタンス化
login_manager = LoginManager()
#アプリをログイン機能を紐付ける
login_manager.init_app(app)

# MARK:ログイン情報保持
#現在のログインユーザーの情報を保持し、必要なときに参照できるようになる。
@login_manager.user_loader
def load_user(userId):
    try:
        return User.query.get(userId)
    except Exception as e:
        print(f"Error ログイン情報保持処理失敗: {e}")
        return None

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
        try:
            user = User.query.all()
        except Exception as e:
            print(f"Error ユーザー情報取得失敗: {e}")
            user = []
        return render_template('index.html', user=user)
    
# MARK: saleDetail
@app.route('/saleDetail/<int:sale_id>', methods=['GET', 'POST'])
def saleDetail(sale_id):
    try:
        # 商品情報をデータベースから取得
        sale = Sale.query.get(sale_id)
        bids = Bid.query.filter_by(saleId=sale_id).all()
        currentPrice = db.session.query(Bid.bidPrice).filter_by(saleId=sale_id).order_by(Bid.bidPrice.desc()).first()
        currentPrice = currentPrice[0] if currentPrice else sale.startingPrice
        categories = ', '.join([category.categoryName for category in sale.categories])
    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
        return "エラーが発生しました", 500

    print(sale)
    print(f"Sale ID: {sale_id}, categories: {categories}")

    if sale is None:
        # 商品が見つからない場合の処理
        return "商品が見つかりません", 404
        
    # 商品の入札終了日時が現在時刻の前であるかどうか
    # 終了していた時の処理↓
    try:
        if sale.finishTime and datetime.now().strftime('%Y/%m/%d %H:%M:%S') > sale.finishTime:
            # 落札者情報の取得
            # 落札金額
            lastAmount = db.session.query(func.max(Bid.bidPrice)).scalar()
            # 落札者userIdの取得
            bidUserId = db.session.query(Bid.userId).filter(Bid.bidPrice == lastAmount).scalar()
        
            db.session.query(Sale).filter(Sale.saleId == sale_id).update({"saleStatus": False})
            db.session.commit()
            print("最大金額（落札金額）:",lastAmount)
            finished = "この作品のオークションは終了しています"
            return render_template('saleDetail.html', sale=sale, bids=bids, currentPrice=currentPrice, categories=categories, finished=finished, bidUserId=bidUserId ,lastAmount=lastAmount)
        
        # 商品なかった時のerror処理
        if sale is None:
            flash('Sale not found', 'error')
            return redirect(url_for('top'))
        
        #現在時刻取得
        dt = datetime.now()
        datetimeStr = datetime.strptime(dt.strftime('%Y/%m/%d %H:%M:%S'), '%Y/%m/%d %H:%M:%S')
        #終了時刻取得
        finishTime = datetime.strptime(sale.finishTime, '%Y/%m/%d %H:%M:%S')
        # 計算（差分）
        timeDifference = finishTime - datetimeStr
        print(timeDifference, type(timeDifference))
        
        # 商品情報をテンプレートに渡す
        return render_template('saleDetail.html', sale=sale, bids=bids, currentPrice=currentPrice, categories=categories, timeDifference=timeDifference)

    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
# MARK: 入札
@app.route('/bid', methods=['POST'])
@login_required
def bid():
    try:
        data = request.get_json()
        userId = session.get('userId')
        sale_id = data.get('saleId')
        amount = data.get('amount') #入札金額
        
        # saleテーブルのcurrentPrice（現在価格）を更新
        sale = Sale.query.filter_by(saleId=sale_id).first()
        sale.currentPrice = amount
    
        print(f"user_id:{userId}, sale_id: {sale_id}, amount: {amount}")

        # Bidテーブルに新しい入札を追加
        new_bid = Bid(userId=userId, saleId=sale_id, bidPrice=amount)
        
        db.session.add(new_bid)
        db.session.commit()
    except Exception as e:
        print(f"Error 入札処理失敗: {e}")
        return jsonify({'success': False, 'message': '入札に失敗しました'}), 500

    return jsonify({'success': True, 'message': '入札が成功しました'})

# MARK: サインアップページ
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
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
        except Exception as e:
            print(f"Error サインアップ処理失敗: {e}")
            return "エラーが発生しました", 500
    
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
        try:
            userName = request.form.get('userName')
            password = request.form.get('password')
            error = "ユーザーネームまたはパスワードが違います。"
            # Userテーブルからusernameに一致するユーザを取得
            user = User.query.filter_by(userName=userName).first()
        except Exception as e:
            print(f"Error ログイン処理失敗: {e}")
            return "エラーが発生しました", 500
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
    
    try:
        sales = Sale.query.all()  # すべての商品を取得
    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
        sales = []
    
    try:
        liked_sales = (
            db.session.query(Like.saleId)
            .filter_by(userId=userId)
            .all()
        )  # ユーザーが過去に「いいね」をした商品IDのリストを取得
        liked_sale_ids = [sale[0] for sale in liked_sales]  # 取得したsale_idをリスト化
        
        likeRankings = db.session.query(Like.saleId, db.func.count(Like.saleId)).group_by(Like.saleId).order_by(db.func.count(Like.saleId).desc()).limit(3).all()
    except Exception as e:
        print(f"Error いいねした商品のID取得失敗: {e}")
        liked_sale_ids = []
    
    #likeRankingsからsaleIdを取り出し、リスト化
    saleIds = [sale[0] for sale in likeRankings]
    
    try:
        #saleIdをもとにSaleテーブルから商品情報を取得
        saleRankings = Sale.query.filter(Sale.saleId.in_(saleIds)).all()
    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
        saleRankings = []
    
    try:
        sales=db.session.query(Sale).all()  
    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
        sales = []      
        
    return render_template('top.html', sales=sales, userId=userId, liked_sale_ids=liked_sale_ids, saleRankings=saleRankings, SAS=SAS)

# MARK: いいね情報受け取りroute
@app.route('/like', methods=['POST'])
def like_sale():
    user_id = request.form['userId']
    sale_id = request.form['saleId']
    
    try:
        # すでにこのユーザーがこの商品に「いいね」をしていないか確認
        existing_like = Like.query.filter_by(saleId=sale_id, userId=user_id).first()
    except Exception as e:
        print(f"Error いいねの確認処理失敗: {e}")
        return jsonify({'error': 'Failed to query existing like'}), 500
    
    if existing_like:
        try:
            # すでに「いいね」している場合は削除
            db.session.delete(existing_like)
            db.session.commit()
        except Exception as e:
            print(f"Error いいねの削除失敗: {e}")
            return jsonify({'error': 'Failed to remove like'}), 500
        action = 'removed'
    else:
        try:
            # 新たに「いいね」を追加
            new_like = Like(userId=user_id, saleId=sale_id)
            db.session.add(new_like)
            db.session.commit()
        except Exception as e:
            print(f"Error いいね追加失敗: {e}")
            return jsonify({'error': 'Failed to add like'}), 500
        action = 'added'
    
    try:
        # 「いいね」された商品に対する「いいね」の数を取得
        like_count = Like.query.filter_by(saleId=sale_id).count()
    except Exception as e:
        print(f"Error いいね数の取得失敗: {e}")
        return jsonify({'error': 'Failed to query like count'}), 500
    
    print(f"Like count for sale {sale_id}: {like_count}")
    return jsonify({'action': action, 'likeCount': like_count})

# MARK: いいね一覧ページ
@app.route('/myLikeList')
@login_required
def myLikeList():
    userId = session.get('userId')
    try:
        # userIdからそのユーザー情報を取得
        user = User.query.get(userId) 
        myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Like.likeId.desc()).all()
        # 入札数の取得
        bidCount = db.session.query(Sale.saleId, func.coalesce(func.count(Bid.bidId), 0).label('bid_count')) \
                    .outerjoin(Bid, Bid.saleId == Sale.saleId) \
                    .join(Like, Like.saleId == Sale.saleId) \
                    .filter(Like.userId == userId) \
                    .group_by(Sale.saleId) \
                    .all()
        # 残り時間の取得
        for sale in myLikeList:
            # finishTimeをdatetime型に変換 (形式: '%Y/%m/%d %H:%M:%S')
            finish_time_str = sale.finishTime
            finish_time = datetime.strptime(finish_time_str, '%Y/%m/%d %H:%M:%S')  # 'YYYY/MM/DD HH:MM:SS' の形式

            # 現在の時刻を取得
            current_time = datetime.now()

            # 残り時間を計算
            remaining_time = finish_time - current_time  # 残り時間
            remaining_seconds = int(remaining_time.total_seconds())  # 秒に変換

            # 残り時間が0秒未満（終了後）の場合
            if remaining_seconds < 0:
                remaining_time_str = "終了"

            else:
                days, remainder = divmod(remaining_seconds, 86400)  # 日数を取得
                hours, remainder = divmod(remainder, 3600)  # 時間を取得
                minutes, seconds = divmod(remainder, 60)  # 分と秒を取得

                remaining_time_str = f"{days}日{hours:02}時間{minutes:02}分"  # 残り時間を表示形式にする
            
            # saleに残り時間を追加
            sale.remaining_time_str = remaining_time_str  # 各商品に残り時間を保持させる
        print(bidCount)
    except Exception as e:
        print(f"Error いいね一覧の取得失敗: {e}")
        myLikeList = []
        bidCount = []
        
    print(myLikeList)
    return render_template('myLikeList.html', user=user, myLikeList=myLikeList, bidCount=bidCount, SAS=SAS)

# MARK: 並び順を渡すurl
@app.route('/sort_products')
def sort_products():
    userId = session.get('userId')
    sort_order = request.args.get('order', 'likeOrder')  # デフォルト値としてprice_ascを設定
    print("並び替え：",sort_order)

    # 並び替えの条件を動的に変更
    if sort_order == 'likedOrder':
        try:
            # いいねした順
            myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Like.likeId.desc()).all()
        except Exception as e:
            print(f"Error いいねした順の並び替え失敗: {e}")
            myLikeList = []
            
    elif sort_order == 'orderCheapPrice':
        try:
            # 価格の安い順
            myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Sale.currentPrice.asc()).all()
        except Exception as e:
            print(f"Error 価格の安い順の並び替え失敗: {e}")
            myLikeList = []
            
    elif sort_order == 'orderHighPrice':
        try:
            # 価格の高い順
            myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Sale.currentPrice.desc()).all()
        except Exception as e:
            print(f"Error 価格の高い順の並び替え失敗: {e}")
            myLikeList = []

    # 入札数の取得
    bidCount = db.session.query(Sale.saleId, func.coalesce(func.count(Bid.bidId), 0).label('bid_count')) \
                .outerjoin(Bid, Bid.saleId == Sale.saleId) \
                .join(Like, Like.saleId == Sale.saleId) \
                .filter(Like.userId == userId) \
                .group_by(Sale.saleId) \
                .all()
    
    # 商品情報を整形
    product_list = []
    for sale in myLikeList:
        # finishTimeをdatetime型に変換 (形式: '%Y/%m/%d %H:%M:%S')
        finish_time_str = sale.finishTime
        finish_time = datetime.strptime(finish_time_str, '%Y/%m/%d %H:%M:%S')  # 'YYYY/MM/DD HH:MM:SS' の形式

        # 現在の時刻を取得
        current_time = datetime.now()

        # 残り時間を計算
        remaining_time = finish_time - current_time  # 残り時間
        remaining_seconds = int(remaining_time.total_seconds())  # 秒に変換

        # 残り時間が0秒未満（終了後）の場合
        if remaining_seconds < 0:
            remaining_time_str = "終了"

        else:
            days, remainder = divmod(remaining_seconds, 86400)  # 日数を取得
            hours, remainder = divmod(remainder, 3600)  # 時間を取得
            minutes, seconds = divmod(remainder, 60)  # 分と秒を取得

            remaining_time_str = f"{days}日{hours:02}時間{minutes:02}分  "  # 残り時間を表示形式にする

        # 商品情報に残り時間を追加
        product_list.append({
            'id': sale.saleId,
            'title': sale.title,
            'currentPrice': sale.currentPrice,
            'filePath': url_for('static', filename=sale.filePath),
            'bidCount': next((bid for sale_id, bid in bidCount if sale_id == sale.saleId), 0),
            'remainingTime': remaining_time_str  # 残り時間を追加
        })

    
    # 結果をJSON形式で返す
    return jsonify(product_list)

# MARK: マイページ
@app.route('/myPage')
@login_required
def myPage():
    userId = session.get('userId')
    try:
        user = User.query.get(userId)
        # session(ログイン状態のuserId)のsaleの行を取り出し、
        # 外部キーのuserIdよりUserテーブルの中のデータを参照できる。
        sales = db.session.query(Sale).join(User).filter_by(userId=userId).all()
    except Exception as e:
        print(f"Error マイページの情報取得失敗: {e}")
        user = None
        sales = []
        
    for sale in sales:
        display_name = sale.user.displayName
        title = sale.title
        print(title)
        print(f"ユーザーの表示名: {display_name}")
    
    try:
        listing_number = db.session.query(Sale).filter(Sale.userId == userId).count()
    except Exception as e:
        print(f"Error 商品のカウントに失敗: {e}")
        listing_number = 0
            
    return render_template('myPage.html', user=user, sales=sales, listingNumber=listing_number, SAS=SAS)

# MARK: canvas→画像変換
def decode_image(image_data):
    try:
        image_data = image_data.split(",")[1]
        return base64.b64decode(image_data)
    except (IndexError, base64.binascii.Error):
        return None

# MARK: 画像保存
# ローカルフォルダに保存
def save_image_to_file(image_bytes, upload_folder):
    try:
        file_name = f"image_{len(os.listdir(upload_folder)) + 1}.png"
        file_path = os.path.join(upload_folder, file_name).replace('\\', '/')
        with open(file_path, 'wb') as f:
            f.write(image_bytes)
        return file_path
    except Exception as e:
        print(f"Error 画像保存失敗: {e}")
        return None
    
# Azure Blob Storageに保存
# def save_image_to_azure(image_bytes):
#     try:
#         # ランダムなファイル名を生成
#         file_name = f"image_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.png"

#         # Azure Blob Storageに画像をアップロード
#         blob_client = container_client.get_blob_client(file_name)
#         blob_client.upload_blob(image_bytes, overwrite=True)

#         # アップロードされた画像のURLを取得
#         blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{file_name}"
#         return blob_url
#     except Exception as e:
#         print(f"Error 画像保存失敗: {e}")
#         return None

# MARK:　出品ページ
@app.route('/add_sale', methods=['POST'])
def add_sale():
    try:
        data = request.get_json()
        image_data = data.get('image')
        time = data.get('time')
        price = data.get('price')
        title = data.get('title')
        postingTime = data.get('postingTime')
        categories = data.get("categories")
        print(title)
        print(postingTime)
        print(categories)
    except Exception as e:
        print(f"Error 出品情報取得失敗: {e}")
        return jsonify({'error': 'Failed to parse request data'}), 400
    
    if not image_data:
        return jsonify({'error': 'No image data provided'}), 400

    image_bytes = decode_image(image_data)
    if not image_bytes:
        return jsonify({'error': 'Invalid image data'}), 400

    # 画像をローカルフォルダに保存
    file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])
    file_path = file_path.replace(app.config['UPLOAD_FOLDER'], 'upload_images')
    
    # try:
    #     # 画像をAzure Blob Storageに保存
    #     blob_url = save_image_to_azure(image_bytes)
    #     if not blob_url:
    #         return jsonify({"error": "Failed to save image"}), 500
    # except Exception as e:
    #     # 保存成功時に画像のURLを返す
    #     return jsonify({"message": "Image uploaded successfully", "image_url": blob_url}), 201


    userId = session.get('userId') # 今使っているユーザーのuserIdの取得
    try:
        user = User.query.get(userId) # userIdからuser情報受け取り
    except Exception as e:
        print(f"Error ユーザー情報取得失敗: {e}")
        return jsonify({'error': 'Failed to query user'}), 500
    
    displayName = user.displayName # displayNameの取得

    #現在時刻取得
    dt = datetime.now()
    datetimeStr = dt.strftime('%Y/%m/%d %H:%M:%S')
    #掲載時間計算
    postingTimePlus = dt + timedelta(minutes=int(postingTime))
    postingTimeStr = postingTimePlus.strftime('%Y/%m/%d %H:%M:%S')
    print("現在時刻：", datetimeStr)
    print("掲載満了時刻：", postingTimeStr)

    try:
        new_sale = Sale(userId=userId, displayName=displayName, title=title, filePath=file_path, startingPrice=price,currentPrice=price, creationTime=time, startingTime=datetimeStr, finishTime=postingTimeStr)
        
         # categories 変数の値に基づいて Category を一度に取得
        category_objects = Category.query.filter(Category.categoryName.in_(categories)).all()
        db.session.add(new_sale)
        db.session.commit()
    except Exception as e:
        print(f"Error 出品処理失敗: {e}")
        return jsonify({'error': 'Failed to create sale'}), 500
    
   

    # 存在しないカテゴリ名のチェック
    found_category_names = {category.categoryName for category in category_objects}
    missing_categories = set(categories) - found_category_names
    if missing_categories:
        # ログを出力するか、エラー処理を追加
        print(f"Warning: The following categories were not found: {missing_categories}")

    try:
        # 中間テーブルにカテゴリーを追加
        new_sale.categories.extend(category_objects)
        new_bid = Bid(userId=userId, saleId=new_sale.saleId, bidPrice=price)
        db.session.add(new_sale, new_bid)
        db.session.commit()
    except Exception as e:
        print(f"Error 中間テーブルへの追加失敗: {e}")
        return jsonify({'error': 'Failed to add categories'}), 500

    return jsonify({'message': 'Sale added successfully'}), 201    

# MARK: 描画ページ
@app.route('/draw')
def draw():
    return render_template('draw.html')

# MARK: 出品ページ処理
@app.route('/result')
def result():
    try:
        # 既存のカテゴリを取得
        categories = Category.query.all()
    except Exception as e:
        print(f"Error カテゴリ取得失敗: {e}")
        categories = []
    
    return render_template('result.html', categories=categories)

@app.route('/contact', methods=['GET', 'POST'])
@login_required
def contact():
    if request.method == 'POST':
        try:
            userId = session.get('userId')
            # フォームからデータを取得
            name = request.form.get('name')
            name_kana = request.form.get('name_kana')
            email = request.form.get('mail')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            # ファイルの処理（もし添付ファイルがある場合）
            file = request.files.get('test')
            file_path = None
            if file and file.filename:
                # ファイル名を安全に保存
                filename = secure_filename(file.filename)
                file_path = os.path.join('uploads', filename)
                file.save(file_path)
            
            # 新しい問い合わせを作成
            new_inquiry = Inquiry(
                userId=userId,
                displayName=name,
                mailAddress=email,
                inquiryContent=message,
                appendFile=file_path
            )
            
            # データベースに保存
            db.session.add(new_inquiry)
            db.session.commit()
            
            flash('お問い合わせを受け付けました。ありがとうございます。', 'success')
            return redirect(url_for('contact'))
            
        except Exception as e:
            print(f"Error お問い合わせ送信失敗: {e}")
            flash('お問い合わせの送信に失敗しました。もう一度お試しください。', 'error')
            db.session.rollback()
            
    return render_template('contact.html')

# # ---- ユーザーデータの仮挿入 ----
# def add_users():
#     dummy_users = [
#         User(userName='user1', displayName='User One', mailAddress='user1@example.com', password='password1'),
#         User(userName='user2', displayName='User Two', mailAddress='user2@example.com', password='password2'),
#         User(userName='user3', displayName='User Three', mailAddress='user3@example.com', password='password3')
#     ]
    
#     db.session.add_all(dummy_users)
#     db.session.commit()

# ---- カテゴリデータの仮挿入 ----
def add_categories():
    dummy_categories = [
        Category(categoryName='キャラクター'),
        Category(categoryName='模写'),
        Category(categoryName='空想'),
        Category(categoryName='抽象'),
        Category(categoryName='カラフル'),
        Category(categoryName='風景'),
        Category(categoryName='動物'),
        Category(categoryName='静物'),
        Category(categoryName='ポートレート'),
    ]
    
    try:
        db.session.add_all(dummy_categories)
        db.session.commit()
    except Exception as e:
        print(f"Error カテゴリ追加処理失敗: {e}")
        db.session.rollback()
        dummy_categories = []
        
    return dummy_categories

# # ---- 商品データの仮挿入 ----
# def add_sales(dummy_categories):    
#     dummy_sales = [
#         Sale(userId=1, displayName='User One', title='iPhone', filePath='0001.png', startingPrice=10000, currentPrice=10000, creationTime='10:00'),
#         Sale(userId=2, displayName='User Two', title='小説', filePath='0002.png', startingPrice=50000, currentPrice=50000, creationTime='10:00')
#     ]
#     dummy_sales[0].categories.append(dummy_categories[0])
#     dummy_sales[1].categories.append(dummy_categories[1])
    
#     db.session.add_all(dummy_sales)
#     db.session.commit()

# MARK: テーブルの作成
if __name__ == '__main__': 
    with app.app_context():
        try:
            # db.drop_all() # テーブルの全削除
            db.create_all()
            # add_users()
            # dummy_categories = add_categories()
            # add_sales(dummy_categories)
        except Exception as e:
            print(f"Error テーブル作成失敗: {e}")
            db.session.rollback()
            db.session.close()
            exit()
    app.run(host='0.0.0.0', port=80, debug=True)