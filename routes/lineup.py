from imports import *
from auth.config import AZURE_STORAGE_SAS

# MARK: 作品一覧ページ
def lineup(app):
    @app.route('/lineup')
    def lineup():
        userId = session.get('userId')
        
        try:
            # 通常の商品一覧を取得(新着順)
            sales = Sale.query.order_by(Sale.saleId.desc()).all()
            
            # いいね情報の取得
            liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
            liked_sale_ids = [sale[0] for sale in liked_sales]
            
        except Exception as e:
            print(f"Error 商品情報取得失敗: {e}")
            sales = []
            liked_sale_ids = []
        
        return render_template('lineup.html', 
                            sales=sales, 
                            userId=userId, 
                            liked_sale_ids=liked_sale_ids, 
                            SAS=AZURE_STORAGE_SAS)