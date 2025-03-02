from imports import *
import pytz 

def saleDetail(app):
    # MARK: saleDetail
    @app.route('/saleDetail/<int:sale_id>', methods=['GET', 'POST'], endpoint='saleDetail_view')
    @login_required
    def saleDetail_view(sale_id):
        try:
            # 商品情報をデータベースから取得
            sale = db.session.query(Sale).get(sale_id)
            bids = Bid.query.filter_by(saleId=sale_id).all()
            currentPrice = db.session.query(Bid.bidPrice).filter_by(saleId=sale_id).order_by(Bid.bidPrice.desc()).first()
            currentPrice = currentPrice[0] if currentPrice else sale.startingPrice
            categories = ', '.join([category.categoryName for category in sale.categories])
            userName = db.session.query(User.userName).filter(User.userId == sale.userId).scalar()
            userIcon = db.session.query(User.iconFilePath).filter(User.userId == sale.userId).scalar()

            bid_userName = {}
            for bid in bids:
                bid_userName[bid.userId] = db.session.query(User.userName).filter(User.userId == bid.userId).scalar()
        except Exception as e:
            print(f"Error 商品情報取得失敗: {e}")
            return "エラーが発生しました", 500

        print(sale)
        print(f"Sale ID: {sale_id}, categories: {categories}")

        if sale is None:
            # 商品が見つからない場合の処理
            return "商品が見つかりません", 404
            
        # 商品の入札終了日時が現在時刻の前であるかどうか
        # 終了していた時の処理↓
        try:
            if sale.finishTime and datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S') > sale.finishTime:
                # 落札者情報の取得
                # 落札金額
                lastAmount = db.session.query(func.max(Bid.bidPrice)).scalar()
                # 落札者userIdの取得
                bidUserId = db.session.query(Bid.userId).filter(Bid.bidPrice == lastAmount).scalar()
            
                db.session.query(Sale).filter(Sale.saleId == sale_id).update({"saleStatus": False})
                db.session.commit()
                print("最大金額（落札金額）:",lastAmount)
                finished = "この作品のオークションは終了しています"
                return render_template('saleDetail.html', sale=sale, bids=bids, currentPrice=currentPrice, categories=categories, finished=finished, bidUserId=bidUserId ,lastAmount=lastAmount, config=app.config)
            
            # 商品なかった時のerror処理
            if sale is None:
                flash('Sale not found', 'error')
                return redirect(url_for('top'))

            # 商品情報をテンプレートに渡す
            return render_template('saleDetail.html', userName=userName, userIcon=userIcon, sale=sale, bids=bids, currentPrice=currentPrice, categories=categories, bid_userName=bid_userName, config=app.config)

        except Exception as e:
            print(f"Error 商品情報取得失敗: {e}")