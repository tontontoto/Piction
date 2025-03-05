from imports import *

# MARK: 描画ページ
def draw(app):
    @app.route('/draw')
    @login_required
    def draw_view():
        return render_template('draw.html')
    

# MARK: 出品ページ処理
def result(app):
    @app.route('/result')
    @login_required
    def result_view():
        try:
            # 既存のカテゴリを取得
            categories = Category.query.all()
            print(categories)

        except Exception as e:
            print(f"Error カテゴリ取得失敗: {e}")
            categories = []
        
        return render_template('result.html', categories=categories)