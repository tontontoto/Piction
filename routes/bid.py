from imports import *

# MARK: 入札
def bid(app):
    @app.route('/bid', methods=['POST'])
    @login_required
    def bid_view():
        try:
            data = request.get_json()
            userId = session.get('userId')
            sale_id = data.get('saleId')
            amount = data.get('amount') #入札金額
            
            # saleテーブルのcurrentPrice（現在価格）を更新
            sale = Sale.query.filter_by(saleId=sale_id).first()
            sale.currentPrice = amount
        
            print(f"user_id:{userId}, sale_id: {sale_id}, amount: {amount}")

            # Bidテーブルに新しい入札を追加
            new_bid = Bid(userId=userId, saleId=sale_id, bidPrice=amount)
            
            db.session.add(new_bid)
            db.session.commit()
            return jsonify({'success': True, 'message': '入札が成功しました'})
        
        except Exception as e:
            print(f"Error 入札処理失敗: {e}")
            return jsonify({'success': False, 'message': '入札に失敗しました'}), 500