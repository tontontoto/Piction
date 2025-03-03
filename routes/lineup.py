from imports import *
from auth.config import AZURE_STORAGE_SAS
from auth.utils import get_recent_sales, get_liked_sales

# MARK: 作品一覧ページ
def lineup(app):
    @app.route('/lineup')
    @login_required
    def lineup():
        userId = session.get('userId')
        
        try:
            # 通常の商品一覧を取得(新着順)
            sales = get_recent_sales()
            
            # いいね情報の取得
            liked_sale_ids = get_liked_sales(userId)
            
        except Exception as e:
            print(f"Error 商品情報取得失敗: {e}")
            sales = []
            liked_sale_ids = []
        
        return render_template('lineup.html', 
                            sales=sales, 
                            userId=userId, 
                            liked_sale_ids=liked_sale_ids, 
                            config=app.config)