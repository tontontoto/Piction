from imports import *

# MARK:ログイン情報保持
#現在のログインユーザーの情報を保持し、必要なときに参照できるようになる。
def load_user(userId):
    try:
        return db.session.get(User, userId)
    except Exception as e:
        print(f"Error ログイン情報保持処理失敗: {e}")
        return None