# MARK:インポート
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from model_sample import db, User, Sale, Category, Bid, Like, Inquiry, WinningBid, PaymentWay, Payment
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from sqlalchemy import func
from azure.storage.blob import BlobServiceClient
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.utils import secure_filename
import random
import string
import os
import base64
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 環境設定の取得
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')

# データベースURLの設定
if ENVIRONMENT == 'local':
    DB_URL = os.getenv('LOCAL_DB_URL')
else:
    DB_URL = os.getenv('AZURE_DB_URL')

# Azure Blob Storage設定
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER')
AZURE_STORAGE_SAS = os.getenv('AZURE_STORAGE_SAS')

# アプリケーション設定
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './static/upload_images')

# MARK:インスタンス化
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Azure Blob Storage クライアントの設定（ローカル環境では無効化）
if ENVIRONMENT == 'azure' and AZURE_STORAGE_CONNECTION_STRING:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER)
        print("Azure Blob Storage connected successfully")
    except Exception as e:
        print(f"Azure Blob Storage connection failed: {e}")
        blob_service_client = None
        container_client = None
else:
    blob_service_client = None
    container_client = None

print(f"現在の環境: {ENVIRONMENT}")
print(f"データベースURL: {DB_URL}")

# ローカル画像保存先フォルダの作成
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

try:
    db.init_app(app)
except Exception as e:
    print(e)
    
bcrypt = Bcrypt()
#インスタンス化
login_manager = LoginManager()
#アプリをログイン機能を紐付ける
login_manager.init_app(app)

# MARK: 管理者画面
class LikeModelView(ModelView):
    # 一覧表示のカラム設定
    column_list = ['likeId', 'user.displayName', 'sale.title']
    
    # 外部キーの表示名を設定
    column_labels = {
        'likeId': 'いいねID',
        'user.displayName': 'ユーザー名',
        'sale.title': '作品タイトル'
    }
    
    # リレーションの表示設定
    column_formatters = {
        'user.displayName': lambda v, c, m, p: m.user.displayName if m.user else '',
        'sale.title': lambda v, c, m, p: m.sale.title if m.sale else ''
    }

class BidModelView(ModelView):
    column_list = ['bidId', 'user.displayName', 'sale.title', 'bidPrice', 'bidTime']
    
    column_labels = {
        'bidId': '入札ID',
        'user.displayName': '入札者',
        'sale.title': '作品タイトル',
        'bidPrice': '入札価格',
        'bidTime': '入札時間'
    }
    
    column_formatters = {
        'user.displayName': lambda v, c, m, p: m.user.displayName if m.user else '',
        'sale.title': lambda v, c, m, p: m.sale.title if m.sale else ''
    }

# 管理画面の設定
admin = Admin(app, name='Piction', template_mode='bootstrap3')
admin.add_view(ModelView(User, db.session, name='ユーザー'))
admin.add_view(ModelView(Sale, db.session, name='出品'))
admin.add_view(ModelView(Category, db.session, name='カテゴリー'))
admin.add_view(BidModelView(Bid, db.session, name='入札履歴'))
admin.add_view(LikeModelView(Like, db.session, name='いいね'))
admin.add_view(ModelView(Inquiry, db.session, name='お問い合わせ'))

# アップロードフォルダの設定
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_ICON_FOLDER'] = './static/upload_icon'
os.makedirs(app.config['UPLOAD_ICON_FOLDER'], exist_ok=True)

# ファイルの拡張子を確認するヘルパー関数
def allowed_file(filename):
    # ファイル名に拡張子が含まれているかを確認
    if '.' in filename:
        # ファイル名を拡張子で分割して、拡張子が許可されたものかを確認
        file_extension = filename.rsplit('.', 1)[1].lower()
        return file_extension in ALLOWED_EXTENSIONS
    return False

# @app.route('/myPage', methods=['GET', 'POST'])
# def upload_file():
#     if request.method == 'POST':
#         if 'file' not in request.files:
#             return 'ファイルが送信されていません'
#         file = request.files['file']
        
#         if file.filename == '':
#             return 'ファイルが選択されていません'
        
#         if file and allowed_file(file.filename):
#             # ファイル名を安全な名前に変更
#             filename = secure_filename(file.filename)
            
#             # 保存先のファイルパスを決定
#             iconFilePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
#             # ファイルを保存    
#             file.save(iconFilePath)
            
#             # データベースにファイルパスを保存
#             new_image = userIcon(iconFilePath=iconFilePath)
#             db.session.add(new_image)
#             db.session.commit()

#             return f'ファイル {filename} がアップロードされ、データベースに保存されました！'
    
#     return render_template('myPage.html')

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

# MARK: Pageエラー
@app.errorhandler(401) # 401: 認証エラー
@app.errorhandler(404) # 404: Not Found エラー
def error_401(error):
    return render_template('error.html'),401 if error.code == 401 else 404

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

            # WinningBidテーブルの更新
            buyerId = db.session.query(Sale).filter(Sale.saleStatus == False)

            # 重複チェック
            existing_winningBid = db.session.query(WinningBid).filter_by(buyerId=bidUserId, saleId=sale_id).first()
            if not existing_winningBid:
                new_winningBid = WinningBid(buyerId=bidUserId, saleId=sale_id)
                db.session.add(new_winningBid)
                db.session.commit()
        
            db.session.query(Sale).filter(Sale.saleId == sale_id).update({"saleStatus": False})
            db.session.commit()
            print("最大金額（落札金額）:",lastAmount)
            finished = "この作品のオークションは終了しています"
            return render_template('saleDetail.html', sale=sale, bids=bids, currentPrice=currentPrice, categories=categories, finished=finished, bidUserId=bidUserId ,lastAmount=lastAmount)
        
        # 商品なかった時のerror処理
        if sale is None:
            flash('Sale not found', 'error')
            return redirect(url_for('top'))

        # 商品情報をテンプレートに渡す
        return render_template('saleDetail.html', sale=sale, bids=bids, currentPrice=currentPrice, categories=categories)

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
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    try:
        if request.method == 'POST':
            # セッションからユーザー情報を削除
            session.clear()
            # ログアウト処理
            logout_user()
            flash('ログアウトしました', 'success')
            return render_template('index.html')
        
        # GETリクエストの場合は確認画面を表示
        return render_template('logout.html')
        
    except Exception as e:
        print(f"Error ログアウト処理失敗: {e}")
        flash('ログアウトに失敗しました', 'error')
        return redirect('/logout')

# MARK: トップページ
@app.route('/top')
@login_required
def top():
    userId = session.get('userId')
    print("userIdです！", userId)
    
    try:
        # 新着順に10件取得
        sales = Sale.query.order_by(Sale.saleId.desc()).limit(10).all()
        
        # 高額商品TOP5を取得（現在価格の高い順）
        topPriceSales = Sale.query.order_by(Sale.currentPrice.desc()).limit(5).all()
        
        # いいね情報の取得
        liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
        liked_sale_ids = [sale[0] for sale in liked_sales]
        
        # いいねランキングの取得
        likeRankings = db.session.query(
            Like.saleId, 
            db.func.count(Like.saleId)
        ).group_by(Like.saleId).order_by(
            db.func.count(Like.saleId).desc()
        ).limit(3).all()
        
        saleIds = [sale[0] for sale in likeRankings]
        saleRankings = Sale.query.filter(Sale.saleId.in_(saleIds)).all()
        
    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
        sales = []
        topPriceSales = []
        liked_sale_ids = []
        saleRankings = []
    
    return render_template('top.html', 
                         sales=sales, 
                         userId=userId, 
                         liked_sale_ids=liked_sale_ids, 
                         saleRankings=saleRankings,
                         topPriceSales=topPriceSales,
                         SAS=AZURE_STORAGE_SAS)
    
@app.route('/update_ranking')
def update_ranking():
    try:
        # いいねランキングの取得
        sales_with_likes = db.session.query(
            Sale,
            func.count(Like.likeId).label('like_count')
        ).join(Like).group_by(Sale).order_by(
            func.count(Like.likeId).desc()
        ).limit(3).all()
        
        saleRankings = [sale for sale, _ in sales_with_likes]
        
        # いいね済み商品の取得
        userId = session.get('userId')
        if userId:
            liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
            liked_sale_ids = [sale[0] for sale in liked_sales]
        else:
            liked_sale_ids = []
            
        # ランキング部分のHTMLを生成
        ranking_html = render_template(
            'top_ranking_partial.html',
            saleRankings=saleRankings,
            liked_sale_ids=liked_sale_ids,
            userId=userId
        )
        
        return jsonify({
            'success': True,
            'html': ranking_html
        })
        
    except Exception as e:
        print(f"Error ランキング更新失敗: {e}")
        return jsonify({
            'success': False,
            'message': 'ランキングの更新に失敗しました'
        }), 500


# MARK: 作品一覧ページ
@app.route('/lineup')
def lineup():
    userId = session.get('userId')
    
    try:
        # 通常の商品一覧を取得(新着順)
        sales = Sale.query.order_by(Sale.saleId.desc()).all()
        
        # いいね情報の取得
        liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
        liked_sale_ids = [sale[0] for sale in liked_sales]
        
    except Exception as e:
        print(f"Error 商品情報取得失敗: {e}")
        sales = []
        liked_sale_ids = []
    
    return render_template('lineup.html', 
                         sales=sales, 
                         userId=userId, 
                         liked_sale_ids=liked_sale_ids, 
                         SAS=AZURE_STORAGE_SAS)

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
        # いいねした商品の情報を取得
        sales = db.session.query(Sale).all()
        # userIdからそのユーザー情報を取得
        user = User.query.get(userId)
        # 自分がいいねした商品の情報を取得
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
    return render_template('myLikeList.html', sales=sales, user=user, myLikeList=myLikeList, bidCount=bidCount, SAS=AZURE_STORAGE_SAS)

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
@app.route('/myPage', methods=['GET', 'POST'])
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
    
    # ユーザーの出品数の取得
    try:
        listingCount = db.session.query(Sale).filter(Sale.userId == userId).count()
    except Exception as e:
        print(f"Error 出品数のカウントに失敗: {e}")
        listingCount = "---"

    # いいねした数の取得
    try:
        likeCount = db.session.query(Like).filter(Like.userId == userId).count()
    except Exception as e:
        print(f"Error いいねした商品のカウントに失敗: {e}")
        likeCount = "---"
    
    # 自分が落札した商品の情報を取得
    myBidList = db.session.query(WinningBid).join(Sale).filter(WinningBid.buyerId == userId).all()

    # 落札した商品の情報を取得
    myBidSales = []
    for bid in myBidList:
        sale = Sale.query.get(bid.saleId)
        myBidSales.append(sale)

    print("落札した商品の一覧", myBidSales)
    
    # 自分が入札した作品を取得
    # 最新のBidを取得するためのサブクエリ
    latest_bid_subquery = (
        db.session.query(
            func.max(Bid.bidId).label("latest_bid_id")
        )
        .join(Sale, Bid.saleId == Sale.saleId)
        .filter(Bid.userId == userId)
        .group_by(Sale.saleId)
        .subquery()
    )

    # 最新のBidを持つSale情報を取得
    my_bids_query = (
        db.session.query(Bid, Sale, User)
        .join(Sale, Bid.saleId == Sale.saleId)
        .join(User, Sale.userId == User.userId)
        .filter(Bid.bidId.in_(latest_bid_subquery))
        .order_by(Bid.bidId.desc())  # 最新のBid順に並べる
        .all()
    )
    
    my_bids = []
    for bid in my_bids_query:
        sale = Sale.query.get(bid.Sale.saleId)
        my_bids.append(sale)
        
    
    # 売上情報の取得
    saleStatus = db.session.query(Sale).filter(Sale.userId == userId, Sale.saleStatus == 0).all()
    sale_ids = [sale.saleId for sale in saleStatus]  
    revenue = db.session.query(func.sum(Payment.amount)).filter(Payment.saleId.in_(sale_ids)).scalar() or 0
    
    # POSTメソッドでフォームが送信されたとき
    if request.method == 'POST':
        displayName = request.form.get('displayName')
        userName = request.form.get('userName')
        mailAddress = request.form.get('mailAddress')

        # 'file'がフォームから送信されているか確認
        if 'file' not in request.files:
            return 'ファイルが送信されていません'

        file = request.files['file']
        iconFilePath = user.iconFilePath  # 既存のアイコンパスを保持

        # 新しいアイコンが送信されている場合
        if file and file.filename != '':
            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_extension = filename.rsplit('.', 1)[1].lower()

                # 新しいファイル名を作成
                new_filename = f"user_icon_{len(os.listdir(app.config['UPLOAD_ICON_FOLDER'])) + 1}.{file_extension}"
                file_path = os.path.join(app.config['UPLOAD_ICON_FOLDER'], new_filename).replace('\\', '/')

                # ディレクトリが存在しない場合、作成する
                os.makedirs(app.config['UPLOAD_ICON_FOLDER'], exist_ok=True)

                # 既存のアイコンがあれば削除（オプション）
                if iconFilePath and os.path.exists(os.path.join(app.config['UPLOAD_ICON_FOLDER'], iconFilePath.split('/')[-1])):
                    try:
                        os.remove(os.path.join(app.config['UPLOAD_ICON_FOLDER'], iconFilePath.split('/')[-1]))
                        print(f"既存のアイコンファイル({iconFilePath})を削除しました。")
                    except Exception as e:
                        print(f"既存のアイコン削除に失敗しました: {e}")

                # 新しい画像ファイルを保存
                try:
                    file.save(file_path)
                    print(f"新しいアイコンが保存されました: {file_path}")
                    iconFilePath = f"upload_icon/{new_filename}"  # 新しいアイコンファイルパス
                except Exception as e:
                    print(f"ファイルの保存に失敗しました: {e}")
                    iconFilePath = None

        # ユーザー情報をデータベースに保存
        try:
            if user:
                # アイコンの更新があった場合のみ新しいアイコンパスを保存
                if iconFilePath:
                    user.iconFilePath = iconFilePath

                # 表示名やユーザー名、メールアドレスも更新する場合があれば
                user.displayName = displayName
                user.userName = userName
                user.mailAddress = mailAddress
                db.session.commit()
                print('ユーザー情報が保存されました！')
            else:
                print('ユーザーが見つかりませんでした。')
        except Exception as e:
            db.session.rollback()
            print(f"データベース保存エラー: {e}")

        # リダイレクトでフォーム送信後の再送信を防ぐ
        return redirect(url_for('myPage'))
        

    return render_template('myPage.html', user=user, sales=sales, listingCount=listingCount, likeCount=likeCount, myBidSales=myBidSales, my_bids=my_bids, revenue=revenue)

# MARK: 落札商品詳細ページ
@app.route('/bidSaleDetail/<int:sale_id>', methods=['GET', 'POST'])
def bidSaleDetail(sale_id):
    print(sale_id)

    if request.method == 'POST':
        sale = Sale.query.get(sale_id)
        saleId = sale.saleId # 商品ID
        winningBidId = WinningBid.query.filter_by(saleId=saleId).first().winningBidId # 落札ID
        PaymentMethod = request.form.get('paymentMethod') # 支払い方法
        paymentWayId = db.session.query(PaymentWay.paymentWayId).filter(PaymentWay.paymentWayName == PaymentMethod).scalar() # 支払い方法ID
        comment = request.form.get('comment') # コメント
        amount = sale.currentPrice # 落札金額
        
        new_payment = Payment(saleId=saleId, winningBidId=winningBidId, paymentWayId=paymentWayId, amount=amount)
        db.session.add(new_payment)
        db.session.commit()
        print(saleId, winningBidId, paymentWayId, comment, amount)
        return render_template('bidConfirmation.html', sale=sale)

    else:
        # Sale の情報を取得
        sale = Sale.query.get(sale_id)
        # 出品者の displayName を取得
        name = db.session.query(User.displayName).filter(User.userId == sale.userId).scalar()    
        # WinningBid を使って buyerId を取得し、購入者の displayName を取得
        buyer_display_name = get_buyer_display_name(sale_id)
        # テンプレートに必要な情報を渡してレンダリング
        return render_template('bidSaleDetail.html', sale=sale, name=name, buyer_display_name=buyer_display_name)

# 特定の saleId に対して、buyerId を持つ User の displayName を取得
def get_buyer_display_name(sale_id):
    try:
        # saleId に関連する WinningBid を取得
        winning_bid = db.session.query(WinningBid).filter_by(saleId=sale_id).first()
        # WinningBid が存在し、buyerId が取得できた場合
        if winning_bid and winning_bid.buyerId:
            # buyerId を使って User を取得
            buyer = User.query.get(winning_bid.buyerId)
            # buyer が存在すれば、その displayName を返す
            if buyer:
                return buyer.displayName
            else:
                return "ユーザー情報が見つかりません"
        else:
            return "該当する落札者がいません"
    except Exception as e:
        print(f"Error: {e}")
        return "エラーが発生しました"

# MARK: 落札確認画面
@app.route('/bidConfirmation/<int:sale_id>')
@login_required
def bidConfirmation(sale_id):
    sale = Sale.query.get(sale_id)
    return render_template('bidConfirmation.html', sale=sale)

# MARK: canvas→画像変換
def decode_image(image_data):
    try:
        image_data = image_data.split(",")[1]
        return base64.b64decode(image_data)
    except (IndexError, base64.binascii.Error):
        return None

# MARK: 画像保存
if ENVIRONMENT == 'local':
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
else:
    # Azure Blob Storageに保存
    def save_image_to_azure(image_bytes):
        try:
            # ランダムなファイル名を生成
            file_name = f"image_{''.join(random.choices(string.ascii_letters + string.digits, k=8))}.png"

            # Azure Blob Storageに画像をアップロード
            blob_client = container_client.get_blob_client(file_name)
            blob_client.upload_blob(image_bytes, overwrite=True)

            # アップロードされた画像のURLを取得
            blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{file_name}"
            return blob_url
        except Exception as e:
            print(f"Error 画像保存失敗: {e}")
            return None

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

    if ENVIRONMENT == 'local':
        # 画像をローカルフォルダに保存
        file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])
        file_path = file_path.replace(app.config['UPLOAD_FOLDER'], 'upload_images')
    else:
        try:
            # 画像をAzure Blob Storageに保存
            blob_url = save_image_to_azure(image_bytes)
            if not blob_url:
                return jsonify({"error": "Failed to save image"}), 500
        except Exception as e:
            # 保存成功時に画像のURLを返す
            return jsonify({"message": "Image uploaded successfully", "image_url": blob_url}), 201


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


# MARK: お問い合わせページ
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

# MARK: 検索機能
# MARK: 検索ページ
@app.route('/search')
def search():
    query = request.args.get('query', '').strip()
    
    try:
        if query:
            # 作品名で検索
            sales = Sale.query.filter(Sale.title.ilike(f'%{query}%')).all()
        else:
            # 検索クエリがない場合は全件取得
            sales = Sale.query.all()
        
        # 入札数の取得
        bid_counts = {}
        for sale in sales:
            bid_counts[sale.saleId] = Bid.query.filter_by(saleId=sale.saleId).count()
        
        return render_template('lineup.html', sales=sales, bidCount=bid_counts, query=query)
        
    except Exception as e:
        print(f"Error 検索処理失敗: {e}")
        return render_template('lineup.html', sales=[], bidCount={}, query=query)


@app.route('/my_winning_bids')
@login_required
def my_winning_bids():
    try:
        userId = session.get('userId')
        
        # ユーザーが落札した作品を取得
        winning_bids_query = db.session.query(
            WinningBid, Sale, User
        ).join(
            Sale, WinningBid.saleId == Sale.saleId
        ).join(
            User, Sale.userId == User.userId
        ).filter(
            WinningBid.buyerId == userId
        ).all()
        
        # クエリ結果をデバッグ出力
        print("クエリ結果:", winning_bids_query)
        
        # タプルからディクショナリに変換
        formatted_bids = []
        for winning_bid, sale, user in winning_bids_query:
            bid_info = {
                'winningBid': winning_bid,
                'sale': sale,
                'user': user
            }
            formatted_bids.append(bid_info)
            
            # デバッグ出力
            print(f"落札ID: {winning_bid.winningBidId}")
            print(f"作品タイトル: {sale.title}")
            print(f"出品者: {user.displayName}")
        
        return render_template('my_winning_bids.html', winning_bids=formatted_bids)
    
    except Exception as e:
        print(f"Error 落札した商品の取得失敗: {e}")
        return "エラーが発生しました", 500

@app.route('/download_artwork/<int:sale_id>', methods=['GET', 'POST'])
@login_required
def download_artwork(sale_id):
    sale = Sale.query.get(sale_id)
    file_path = os.path.join(app.root_path, "static", sale.filePath) 
    
    print(f"ファイルパス: {sale.filePath}")

    try:
        f = open(file_path, 'rb') 
        print(f"ファイルダウンロード成功: {file_path}")
        return send_file(f, as_attachment=True, download_name=f"{sale.title}.png")
        
    except Exception as e:
        print(f"Error: {e}")
        print('ダウンロードに失敗しました', 'error')
        return redirect(url_for('myPage'))

# ---- ユーザーデータの仮挿入 ----
def add_users():
    dummy_users = [
        User(userName='artist1', displayName='山田太郎', mailAddress='yamada@example.com', password='111111'),
        User(userName='artist2', displayName='鈴木花子', mailAddress='suzuki@example.com', password='222222'),
        User(userName='artist3', displayName='佐藤一郎', mailAddress='sato@example.com', password='333333'),
        User(userName='artist4', displayName='田中美咲', mailAddress='tanaka@example.com', password='444444'),
        User(userName='artist5', displayName='高橋健一', mailAddress='takahashi@example.com', password='555555')
    ]
    
    db.session.add_all(dummy_users)
    db.session.commit()

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

# ---- 商品データの仮挿入 ----
def add_sales(dummy_categories):    
    dummy_sales = [
        Sale(
            userId=1, 
            displayName='山田太郎', 
            title='一眼レフ', 
            filePath='upload_images/camera.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='10:00',
            startingTime='2024/03/20 10:00:00',
            finishTime='2025/04/20 10:00:00'
        ),
        Sale(
            userId=2, 
            displayName='鈴木花子', 
            title='パソコン', 
            filePath='upload_images/pc.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='11:30',
            startingTime='2024/03/20 11:30:00',
            finishTime='2025/04/20 11:30:00'
        ),
        Sale(
            userId=3, 
            displayName='佐藤一郎', 
            title='ゾウ', 
            filePath='upload_images/elephant.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='12:45',
            startingTime='2024/03/20 12:45:00',
            finishTime='2025/04/20 12:45:00'
        ),
        Sale(
            userId=4, 
            displayName='田中美咲', 
            title='お魚', 
            filePath='upload_images/fish2.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='14:15',
            startingTime='2024/03/20 14:15:00',
            finishTime='2025/04/20 14:15:00'
        ),
        Sale(
            userId=5, 
            displayName='高橋健一', 
            title='雪だるま', 
            filePath='upload_images/snowman.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
        Sale(
            userId=5, 
            displayName='高橋健一', 
            title='いちご', 
            filePath='upload_images/strawberry.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
        Sale(
            userId=5, 
            displayName='高橋健一', 
            title='タピオカ', 
            filePath='upload_images/tapioca.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
        Sale(
            userId=1, 
            displayName='山田太郎', 
            title='ヨット', 
            filePath='upload_images/yacht.png', 
            startingPrice=120, 
            currentPrice=120, 
            creationTime='15:30',
            startingTime='2024/03/20 15:30:00',
            finishTime='2025/04/20 15:30:00'
        ),
    ]

    # カテゴリーの割り当て
    dummy_sales[0].categories.extend([dummy_categories[5], dummy_categories[2]])  # 風景、空想
    dummy_sales[1].categories.extend([dummy_categories[4], dummy_categories[7]])  # カラフル、静物
    dummy_sales[2].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[3].categories.extend([dummy_categories[5], dummy_categories[2]])  # 風景、空想
    dummy_sales[4].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[5].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[6].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    dummy_sales[7].categories.extend([dummy_categories[5], dummy_categories[4]])  # 風景、カラフル
    
    db.session.add_all(dummy_sales)
    db.session.commit()

# MARK: 支払い方法データの挿入
def add_payment_methods():
    dummy_payment_methods = [
        PaymentWay(paymentWayName='現金'),
        PaymentWay(paymentWayName='クレジットカード'),
        PaymentWay(paymentWayName='コンビニ'),
        PaymentWay(paymentWayName='PayPay')
    ]
    db.session.add_all(dummy_payment_methods)
    db.session.commit()

# MARK: テーブルの作成
if __name__ == '__main__': 
    with app.app_context():
        try:
            # db.drop_all()  # テーブルの全削除
            db.create_all()
            # dummy_users = add_users()
            # dummy_categories = add_categories()
            # add_sales(dummy_categories)
            # add_payment_methods()
        except Exception as e:
            print(f"Error テーブル作成失敗: {e}")
            db.session.rollback()
            db.session.close()
            exit()
    app.run(host='0.0.0.0', port=80, debug=True)