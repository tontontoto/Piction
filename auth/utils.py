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
