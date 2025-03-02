from imports import *

# MARK: 検索機能,検索ページ
def search(app):
    @app.route('/search')
    def search_view():
        query = request.args.get('query', '').strip()
        
        try:
            if query:
                # 作品名で検索
                sales = Sale.query.filter(Sale.title.ilike(f'%{query}%')).all()
            else:
                # 検索クエリがない場合は全件取得
                sales = Sale.query.all()
            
            # 入札数の取得
            bid_counts = {}
            for sale in sales:
                bid_counts[sale.saleId] = Bid.query.filter_by(saleId=sale.saleId).count()
            
            return render_template('lineup.html', sales=sales, bidCount=bid_counts, query=query)
            
        except Exception as e:
            print(f"Error 検索処理失敗: {e}")
            return render_template('lineup.html', sales=[], bidCount={}, query=query, config=app.config)