# MARK:== auth ==
from imports import *
from auth.config import *
from auth.azure_blob import connect_to_azure_blob
from auth.img_helper import allowed_file
from auth.admin import init_admin
from auth.user_loader import load_user
from auth.like import like
from auth.update_ranking import update_ranking

# MARK:== routes ==
from routes.welcome import welcome
from routes.login_signup_logout import login, signup, logout
from routes.top import top
from routes.search import search
from routes.mypage import mypage
from routes.my_winning_bids import myWinningBids
from routes.draw import draw, result
from routes.add_sale import add_sale
from routes.sale_detail import saleDetail
from routes.bid import bid
from routes.myLikeList import myLikeList, sort_products
from routes.lineup import lineup
from routes.bid_sale_detail import *
from routes.download_artwork import download_artwork

from routes.contact import contact

# MARK:== database ==
from database.insert_data import add_payment_methods
from database.insert_fake_data import *

# MARK:== error ==
from errors.error_handlers import *

# == インスタンス作成 ==
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_ICON_FOLDER'] = UPLOAD_ICON_FOLDER
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['IS_LOCAL'] = True if ENVIRONMENT == 'local' else False
# Secureなセッション管理
SESSION_COOKIE_HTTPONLY = True  # JavaScriptからアクセス不可
SESSION_COOKIE_SECURE = True    # HTTPSでのみ送信（
SESSION_COOKIE_SAMESITE = 'Lax'  # クロスサイトリクエストを制限

# == ローカル画像保存先フォルダの作成 ==
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(app.config['UPLOAD_ICON_FOLDER'], exist_ok=True)

# Azure Blob Storage接続
blob_service_client, container_client = connect_to_azure_blob()

# DB設定
try:
    db.init_app(app)
except Exception as e:
    print(e)

bcrypt = Bcrypt()
#インスタンス化
login_manager = LoginManager()
#アプリをログイン機能を紐付ける
login_manager.init_app(app)

# 管理画面初期化
init_admin(app)
# いいね機能
like(app)
# ランキングアップデート機能
update_ranking(app)

# ログイン機能設定
login_manager = LoginManager(app)
login_manager.login_view = '/'
#現在のログインユーザーの情報を保持
login_manager.user_loader(load_user)

# MARK:==ROUTES==
#welcome
welcome(app)
# login
login(app)
# signup
signup(app)
# logout
logout(app)
# top
top(app)
# search
search(app)
# mypage
mypage(app)
# myWinningBids
myWinningBids(app)
# draw
draw(app)
# result
result(app)
# add_sale
add_sale(app)
# sale_detail
saleDetail(app)
# bid
bid(app)
# myLikeList
myLikeList(app)
# sort_products
sort_products(app)
# lineup
lineup(app)
# bidSaleDetail
bidSaleDetail(app)
# bidConfirmation
bidConfirmation(app)
# download_artwork
download_artwork(app)
# contact
contact(app)
# error_handler
error_handler(app)


# MARK:テーブルの作成
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