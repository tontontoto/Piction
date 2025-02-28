from imports import *
from auth.config import AZURE_STORAGE_SAS
from auth.utils import get_recent_sales, get_top_price_sales, get_liked_sales, get_like_rankings

# MARK: トップページ
def top(app):
    @app.route('/top')
    @login_required
    def top_view():
        userId = session.get('userId')
        print("userIdです！", userId)
        
        try:
            # 最新商品情報の取得
            sales = get_recent_sales(10)
            # 最新商品情報の取得
            topPriceSales = get_top_price_sales(10)
            # いいね情報の取得
            liked_sale_ids = get_liked_sales(userId)
            # いいねランキングの取得
            saleRankings = get_like_rankings() 
            
        except Exception as e:
            print(f"Error 商品情報取得失敗: {e}")
            sales = []
            topPriceSales = []
            liked_sale_ids = []
            saleRankings = []
            return redirect(url_for('top'))
        
        return render_template('top.html', 
                            sales=sales, 
                            userId=userId, 
                            liked_sale_ids=liked_sale_ids, 
                            saleRankings=saleRankings,
                            topPriceSales=topPriceSales,
                            config=app.config
                            )