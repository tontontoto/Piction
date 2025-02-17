from imports import *

# MARK: 落札した商品一覧処理
def myWinningBids(app):
    @app.route('/my_winning_bids')
    @login_required
    def my_winning_bids_view():
        try:
            userId = session.get('userId')
            
            # ユーザーが落札した作品を取得
            winning_bids_query = db.session.query(
                WinningBid, Sale, User
            ).join(
                Sale, WinningBid.saleId == Sale.saleId
            ).join(
                User, Sale.userId == User.userId
            ).filter(
                WinningBid.buyerId == userId
            ).all()
            
            # クエリ結果をデバッグ出力
            print("クエリ結果:", winning_bids_query)
            
            # タプルからディクショナリに変換
            formatted_bids = []
            for winning_bid, sale, user in winning_bids_query:
                bid_info = {
                    'winningBid': winning_bid,
                    'sale': sale,
                    'user': user
                }
                formatted_bids.append(bid_info)
                
                # デバッグ出力
                print(f"落札ID: {winning_bid.winningBidId}")
                print(f"作品タイトル: {sale.title}")
                print(f"出品者: {user.displayName}")
            
            return render_template('my_winning_bids.html', winning_bids=formatted_bids)
        
        except Exception as e:
            print(f"Error 落札した商品の取得失敗: {e}")
            return "エラーが発生しました", 500
