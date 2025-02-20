from imports import *


# === 各静的機能関数 ===
# ユーザーのログイン処理
def authenticate_user(userName):
    # Userテーブルからusernameに一致するユーザを取得
    user = User.query.filter_by(userName=userName).first()
    return user

# ユーザーの作成処理
def create_user(userName, displayName, mailAddress, password):
    hashdPassword = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(userName=userName, displayName=displayName, mailAddress=mailAddress, password=hashdPassword)
    db.session.add(new_user)
    db.session.commit()
    return new_user

# ユーザーのセッションにIDを保存する処理
def login_user_session(user):
    session['userId'] = user.userId
    login_user(user)


def get_recent_sales(count):
    return Sale.query.order_by(Sale.saleId.desc()).limit(count).all()

def get_top_price_sales(count):
    return Sale.query.order_by(Sale.currentPrice.desc()).limit(count).all()

def get_liked_sales(userId):
    liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
    return [sale[0] for sale in liked_sales]

def get_like_rankings():
    likeRankings = db.session.query(
        Like.saleId, 
        db.func.count(Like.saleId)
    ).group_by(Like.saleId).order_by(
        db.func.count(Like.saleId).desc()
    ).limit(3).all()
    
    saleIds = [sale[0] for sale in likeRankings]
    return Sale.query.filter(Sale.saleId.in_(saleIds)).all()