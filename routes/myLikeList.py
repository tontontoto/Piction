from imports import *
from auth.config import AZURE_STORAGE_SAS
import pytz

# MARK: いいね一覧ページ
def myLikeList(app):
    @app.route('/myLikeList')
    @login_required
    def myLikeList_view():
        userId = session.get('userId')
        try:
            # いいねした商品の情報を取得
            sales = db.session.query(Sale).all()
            # userIdからそのユーザー情報を取得
            user = User.query.get(userId)
            # 自分がいいねした商品の情報を取得
            myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Like.likeId.desc()).all()
            # 入札数の取得
            bidCount = db.session.query(Sale.saleId, func.coalesce(func.count(Bid.bidId), 0).label('bid_count')) \
                        .outerjoin(Bid, Bid.saleId == Sale.saleId) \
                        .join(Like, Like.saleId == Sale.saleId) \
                        .filter(Like.userId == userId) \
                        .group_by(Sale.saleId) \
                        .all()
            # 残り時間の取得
            for sale in myLikeList:
                # finishTimeをdatetime型に変換 (形式: '%Y/%m/%d %H:%M:%S')
                finish_time_str = sale.finishTime
                finish_time = datetime.strptime(finish_time_str, '%Y/%m/%d %H:%M:%S')  # 'YYYY/MM/DD HH:MM:SS' の形式

                # 現在の時刻を取得
                japan_timezone = pytz.timezone('Asia/Tokyo')
                finish_time = japan_timezone.localize(finish_time)
                
                # 現在の時刻を取得
                current_time = datetime.now(japan_timezone)

                # 残り時間を計算
                remaining_time = finish_time - current_time  # 残り時間
                remaining_seconds = int(remaining_time.total_seconds())  # 秒に変換

                # 残り時間が0秒未満（終了後）の場合
                if remaining_seconds < 0:
                    remaining_time_str = "終了"

                else:
                    days, remainder = divmod(remaining_seconds, 86400)  # 日数を取得
                    hours, remainder = divmod(remainder, 3600)  # 時間を取得
                    minutes, seconds = divmod(remainder, 60)  # 分と秒を取得

                    remaining_time_str = f"{days}日{hours:02}時間{minutes:02}分"  # 残り時間を表示形式にする
                
                # saleに残り時間を追加
                sale.remaining_time_str = remaining_time_str  # 各商品に残り時間を保持させる
            print(bidCount)
        except Exception as e:
            print(f"Error いいね一覧の取得失敗: {e}")
            myLikeList = []
            bidCount = []
            
        print(myLikeList)
        return render_template('myLikeList.html', sales=sales, user=user, myLikeList=myLikeList, bidCount=bidCount, config=app.config)

# MARK: 並び順を渡すurl
def sort_products(app):
    @app.route('/sort_products')
    def sort_products_view():
        userId = session.get('userId')
        sort_order = request.args.get('order', 'likeOrder')  # デフォルト値としてprice_ascを設定
        print("並び替え：",sort_order)

        # 並び替えの条件を動的に変更
        if sort_order == 'likedOrder':
            try:
                # いいねした順
                myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Like.likeId.desc()).all()
            except Exception as e:
                print(f"Error いいねした順の並び替え失敗: {e}")
                myLikeList = []
                
        elif sort_order == 'orderCheapPrice':
            try:
                # 価格の安い順
                myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Sale.currentPrice.asc()).all()
            except Exception as e:
                print(f"Error 価格の安い順の並び替え失敗: {e}")
                myLikeList = []
                
        elif sort_order == 'orderHighPrice':
            try:
                # 価格の高い順
                myLikeList = db.session.query(Sale).join(Like).filter(Like.userId == userId).order_by(Sale.currentPrice.desc()).all()
            except Exception as e:
                print(f"Error 価格の高い順の並び替え失敗: {e}")
                myLikeList = []

        # 入札数の取得
        bidCount = db.session.query(Sale.saleId, func.coalesce(func.count(Bid.bidId), 0).label('bid_count')) \
                    .outerjoin(Bid, Bid.saleId == Sale.saleId) \
                    .join(Like, Like.saleId == Sale.saleId) \
                    .filter(Like.userId == userId) \
                    .group_by(Sale.saleId) \
                    .all()
        
        # 商品情報を整形
        product_list = []
        for sale in myLikeList:
            # finishTimeをdatetime型に変換 (形式: '%Y/%m/%d %H:%M:%S')
            finish_time_str = sale.finishTime
            finish_time = datetime.strptime(finish_time_str, '%Y/%m/%d %H:%M:%S')  # 'YYYY/MM/DD HH:MM:SS' の形式

            # 現在の時刻を取得
            current_time = datetime.now(pytz.timezone('Asia/Tokyo'))

            # 残り時間を計算
            remaining_time = finish_time - current_time  # 残り時間
            remaining_seconds = int(remaining_time.total_seconds())  # 秒に変換

            # 残り時間が0秒未満（終了後）の場合
            if remaining_seconds < 0:
                remaining_time_str = "終了"

            else:
                days, remainder = divmod(remaining_seconds, 86400)  # 日数を取得
                hours, remainder = divmod(remainder, 3600)  # 時間を取得
                minutes, seconds = divmod(remainder, 60)  # 分と秒を取得

                remaining_time_str = f"{days}日{hours:02}時間{minutes:02}分  "  # 残り時間を表示形式にする

            # 商品情報に残り時間を追加
            product_list.append({
                'id': sale.saleId,
                'title': sale.title,
                'currentPrice': sale.currentPrice,
                'filePath': url_for('static', filename=sale.filePath),
                'bidCount': next((bid for sale_id, bid in bidCount if sale_id == sale.saleId), 0),
                'remainingTime': remaining_time_str  # 残り時間を追加
            })

        
        # 結果をJSON形式で返す
        print("並び替え後のmyLikeList:", myLikeList)
        return jsonify(product_list)
