from imports import *

# ランキングのアップデート機能
def update_ranking(app):
    @app.route('/update_ranking')
    def update_ranking_view():
        try:
            # いいねランキングの取得
            sales_with_likes = db.session.query(
                Sale,
                func.count(Like.likeId).label('like_count')
            ).join(Like).group_by(Sale).order_by(
                func.count(Like.likeId).desc()
            ).limit(3).all()
            
            saleRankings = [sale for sale, _ in sales_with_likes]
            
            # いいね済み商品の取得
            userId = session.get('userId')
            if userId:
                liked_sales = db.session.query(Like.saleId).filter_by(userId=userId).all()
                liked_sale_ids = [sale[0] for sale in liked_sales]
            else:
                liked_sale_ids = []
                
            # ランキング部分のHTMLを生成
            ranking_html = render_template(
                'top_ranking_partial.html',
                saleRankings=saleRankings,
                liked_sale_ids=liked_sale_ids,
                userId=userId
            )
            
            return jsonify({
                'success': True,
                'html': ranking_html
            })
            
        except Exception as e:
            print(f"Error ランキング更新失敗: {e}")
            return jsonify({
                'success': False,
                'message': 'ランキングの更新に失敗しました'
            }), 500
