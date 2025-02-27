from imports import *

# MARK: 描画ページ
def draw(app):
    @app.route('/draw')
    def draw_view():
        return render_template('draw.html')
    

# MARK: 出品ページ処理
def result(app):
    @app.route('/result')
    def result_view():
        try:
            # 既存のカテゴリを取得
            categories = Category.query.all()
            print(categories)

            # 一週間取得
            today = datetime.now()
            one_weeks = [(today + timedelta(days=i)).strftime('%m月%d日') for i in range(7)]
            print(one_weeks)
            # 時間取得
            times_list = ['0時~1時','1時~2時','2時~3時','3時~4時','4時~5時','5時~6時','6時~7時','7時~8時','8時~9時','9時~10時','10時~11時','11時~12時']

        except Exception as e:
            print(f"Error カテゴリ取得失敗: {e}")
            categories = []
        
        return render_template('result.html', categories=categories, one_weeks=one_weeks, times_list=times_list)