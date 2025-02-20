from imports import *
from auth.decorators import logout_required

#　MARK: Welcomeページ 
def welcome(app):
    @app.route('/', methods=['GET', 'POST'])
    @logout_required
    def welcome_view():      
        if request.method == 'GET':
            try:
                user = User.query.all()
            except Exception as e:
                print(f"Error ユーザー情報取得失敗: {e}")
                user = []
            return render_template('index.html', user=user)