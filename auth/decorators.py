from imports import *
from functools import wraps

# ログインしているユーザに対してのアクセス制限をかけるデコレータ
def logout_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # セッションにユーザーIDがある場合、リダイレクト
        if 'userId' in session:
            # ログイン後にアクセス可能ページにリダイレクト
            return redirect(url_for('top_view'))  
        return f(*args, **kwargs)
    return decorated_function