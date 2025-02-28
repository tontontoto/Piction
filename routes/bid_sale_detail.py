from imports import *

# MARK: 落札商品詳細ページ
def bidSaleDetail(app):
    @app.route('/bidSaleDetail/<int:sale_id>', methods=['GET', 'POST'])
    @login_required
    def bidSaleDetail_view(sale_id):
        print(sale_id)
        if request.method == 'POST':
            sale = db.session.query(Sale).get(sale_id)
            saleId = sale.saleId # 商品ID
            winningBidId = WinningBid.query.filter_by(saleId=saleId).first().winningBidId # 落札ID
            PaymentMethod = request.form.get('paymentMethod') # 支払い方法
            paymentWayId = db.session.query(PaymentWay.paymentWayId).filter(PaymentWay.paymentWayName == PaymentMethod).scalar() # 支払い方法ID
            comment = request.form.get('comment') # コメント
            amount = sale.currentPrice # 落札金額
            
            new_payment = Payment(saleId=saleId, winningBidId=winningBidId, paymentWayId=paymentWayId, amount=amount)
            db.session.add(new_payment)
            db.session.commit()
            print(saleId, winningBidId, paymentWayId, comment, amount)
            return render_template('bidConfirmation.html', sale=sale, config=app.config)

        else:
            # Sale の情報を取得
            sale = db.session.query(Sale).get(sale_id)
            # 出品者の displayName を取得
            name = db.session.query(User.displayName).filter(User.userId == sale.userId).scalar()    
            # WinningBid を使って buyerId を取得し、購入者の displayName を取得
            buyer_display_name = get_buyer_display_name(sale_id)
            # テンプレートに必要な情報を渡してレンダリング
            return render_template('bidSaleDetail.html', sale=sale, name=name, buyer_display_name=buyer_display_name, config=app.config)

# 特定の saleId に対して、buyerId を持つ User の displayName を取得
def get_buyer_display_name(sale_id):
    try:
        # saleId に関連する WinningBid を取得
        winning_bid = db.session.query(WinningBid).filter_by(saleId=sale_id).first()
        # WinningBid が存在し、buyerId が取得できた場合
        if winning_bid and winning_bid.buyerId:
            # buyerId を使って User を取得
            buyer = db.session.query(User).get(winning_bid.buyerId)
            # buyer が存在すれば、その displayName を返す
            if buyer:
                return buyer.displayName
            else:
                return "ユーザー情報が見つかりません"
        else:
            return "該当する落札者がいません"
    except Exception as e:
        print(f"Error: {e}")
        return "エラーが発生しました"


# MARK: 落札確認画面
def bidConfirmation(app):
    @app.route('/bidConfirmation/<int:sale_id>')
    @login_required
    def bidConfirmation_view(sale_id):
        sale = Sale.query.get(sale_id)
        return render_template('bidConfirmation.html', sale=sale, config=app.config)