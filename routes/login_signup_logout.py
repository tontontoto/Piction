from imports import *
from auth.utils import *
from auth.decorators import logout_required

# MARK: ログインページ
def login(app): 
    @app.route('/login', methods=['GET', 'POST'])
    @logout_required
    def login_view():
        if request.method == 'POST':
            try:
                userName = request.form.get('userName')
                password = request.form.get('password')
                error = "ユーザーネームまたはパスワードが違います。"
                # Userテーブルからusernameに一致するユーザを取得
                user = authenticate_user(userName)

                if user and bcrypt.check_password_hash(user.password, password):  # userがNoneでないかも確認
                    print("成功")
                    # sessionに保存
                    login_user_session(user)
                    return redirect('/top')
                else:
                    # ユーザーネームまたはパスワードが違う時の処理
                    return render_template('login.html', error=error)
            
            except Exception as e:
                print(f"Error ログイン処理失敗: {e}")
                flash("エラーが発生しました", 500)
                return render_template('login.html')
        else:
            # method='GET'のとき
            return render_template('login.html')
        
# MARK: サインアップページ
def signup(app):
    @app.route('/signup', methods=['GET', 'POST'])
    def signup_view():
        if request.method == 'POST':
            try:
                userName = request.form.get('userName')
                displayName = request.form.get('displayName')
                mailAddress = request.form.get('mailAddress')
                password = request.form.get('password')
                # privacyPolicy = request.form.get('privacyPolicy')

                # ユーザーの作成処理
                new_user = create_user(userName, displayName, mailAddress, password)
                # ユーザーIDをセッションに保存　-> 後からIDから参照できるようになる
                login_user_session(new_user)
                return redirect('/top')
            
            except Exception as e:
                print(f"Error サインアップ処理失敗: {e}")
                flash("エラーが発生しました", 500)
                return redirect('/signup')
        
        else:
            return render_template('signup.html')

# MARK: ログアウトページ
def logout(app):
    @app.route('/logout', methods=['GET', 'POST'])
    @login_required
    def logout_view():
        if request.method == 'POST':
            try:
                session.clear() # セッションからユーザー情報を削除
                logout_user() # ログアウト処理
                flash('ログアウトしました', 'success')
                return render_template('index.html')
            except Exception as e:
                print(f"Error ログアウト処理失敗: {e}")
                flash('ログアウトに失敗しました', 'error')
                return redirect('/logout')
        else:
            # GETリクエストの場合は確認画面を表示
            return render_template('logout.html')
            
        