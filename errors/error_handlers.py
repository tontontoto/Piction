from imports import *

def error_handler(app):
    # MARK: エラーハンドラ
    @app.errorhandler(401)  # 401: 認証エラー
    @app.errorhandler(404)  # 404: Not Found エラー
    def error(error):
        # 401 と 404 エラーで異なる処理を行う
        if error.code == 401:
            return render_template('error.html', error_message="認証エラー"), 401
        elif error.code == 404:
            return render_template('error.html', error_message="ページが見つかりません"), 404
        return render_template('error.html'), error.code