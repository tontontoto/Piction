from imports import *

# MARK: 落札商品詳細ページ
def bidSaleDetail(app):
    @app.route('/bidSaleDetail/<int:sale_id>', methods=['GET', 'POST'])
    @login_required
    def bidSaleDetail_view(sale_id):
        print(f"リクエストされたsale_id: {sale_id}")
        sale = db.session.query(Sale).get(sale_id)
        if not sale:
            flash('商品が見つかりません', 'error')
            return redirect(url_for('top_view'))
        
        saleId = sale.saleId  # 商品ID
        
        # 支払い完了状態の確認
        winning_bid = WinningBid.query.filter_by(saleId=saleId).first()
        payment = Payment.query.filter_by(saleId=saleId).first()
        
        # 支払いが完了しているか確認
        if payment:
            print(f"支払いが完了しています saleId:{saleId}")
            return redirect(url_for('bidConfirmation_view', sale_id=sale_id))
        
        # POSTリクエスト処理（支払い情報登録）
        if request.method == 'POST':
            try:
                PaymentMethod = request.form.get('paymentMethod')  # 支払い方法
                paymentWayId = db.session.query(PaymentWay.paymentWayId).filter(PaymentWay.paymentWayName == PaymentMethod).scalar()
                comment = request.form.get('comment')  # コメント
                amount = sale.currentPrice  # 落札金額
                
                # 落札者情報の取得
                lastBid = db.session.query(Bid).filter_by(saleId=saleId).order_by(Bid.bidPrice.desc()).first()
                if not lastBid:
                    flash('入札情報が見つかりません', 'error')
                    return render_template('bidSaleDetail.html', sale=sale, config=app.config)
                
                bidUserId = lastBid.userId
                
                # WinningBid作成（存在しない場合のみ）
                if not winning_bid:
                    winning_bid = WinningBid(buyerId=bidUserId, saleId=saleId, sellerId=sale.userId)
                    db.session.add(winning_bid)
                    db.session.commit()
                
                # WinningBidを再取得してIDを確認
                winning_bid = WinningBid.query.filter_by(saleId=saleId).first()
                
                # Payment作成
                new_payment = Payment(
                    saleId=saleId, 
                    winningBidId=winning_bid.winningBidId, 
                    paymentWayId=paymentWayId, 
                    amount=amount
                )
                db.session.add(new_payment)
                db.session.commit()
                
                print(f"支払い完了: saleId={saleId}, winningBidId={winning_bid.winningBidId}")
                return redirect(url_for('bidConfirmation_view', sale_id=sale_id))
                
            except Exception as e:
                db.session.rollback()
                print(f"支払い処理エラー: {e}")
                flash('支払い処理中にエラーが発生しました', 'error')
        
        # GETリクエスト処理（表示）
        # 出品者名を取得
        name = db.session.query(User.displayName).filter(User.userId == sale.userId).scalar()
        # 落札者名を取得（落札がある場合）
        buyer_display_name = get_buyer_display_name(sale_id)
        
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