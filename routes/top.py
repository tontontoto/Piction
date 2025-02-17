from imports import *
from auth.config import AZURE_STORAGE_SAS

# MARK: トップページ
def top(app):
    @app.route('/top')
    @login_required
    def top_view():
        userId = session.get('userId')
        print("userIdです！", userId)
        
        try:
            # 新着順に10件取得
            sales = Sale.query.order_by(Sale.saleId.desc()).limit(10).all()
            
            # 高額商品TOP5を取得（現在価格の高い順）
            topPriceSales = Sale.query.order_by(Sale.currentPrice.desc()).limit(5).all()
            
            # いいね情報の取得
            liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
            liked_sale_ids = [sale[0] for sale in liked_sales]
            
            # いいねランキングの取得
            likeRankings = db.session.query(
                Like.saleId, 
                db.func.count(Like.saleId)
            ).group_by(Like.saleId).order_by(
                db.func.count(Like.saleId).desc()
            ).limit(3).all()
            
            saleIds = [sale[0] for sale in likeRankings]
            saleRankings = Sale.query.filter(Sale.saleId.in_(saleIds)).all()
            
        except Exception as e:
            print(f"Error 商品情報取得失敗: {e}")
            sales = []
            topPriceSales = []
            liked_sale_ids = []
            saleRankings = []
        
        return render_template('top.html', 
                            sales=sales, 
                            userId=userId, 
                            liked_sale_ids=liked_sale_ids, 
                            saleRankings=saleRankings,
                            topPriceSales=topPriceSales,
                            SAS=AZURE_STORAGE_SAS
                            )