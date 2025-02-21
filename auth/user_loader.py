from imports import *
from app import db, login_manager, logger

# MARK:ログイン情報保持
#現在のログインユーザーの情報を保持し、必要なときに参照できるようになる。
# def load_user(userId):
#     try:
#         return User.query.get(userId)
#     except Exception as e:
#         print(f"Error ログイン情報保持処理失敗: {e}")
#         return None
@login_manager.user_loader
def load_user(user_id: int):
    """ ユーザーIDをもとにユーザーをロードする """
    try:
        return db.session.get(User, user_id)
    except Exception as e:
        logger.error(f"Error ログイン情報保持処理失敗: {e}")
        return None