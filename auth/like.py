from imports import *

# MARK: いいね情報受け取りroute
def like(app):
    @app.route('/like', methods=['POST'])
    def like_sale_view():
        user_id = request.form['userId']
        sale_id = request.form['saleId']
        
        try:
            # すでにこのユーザーがこの商品に「いいね」をしていないか確認
            existing_like = Like.query.filter_by(saleId=sale_id, userId=user_id).first()
        except Exception as e:
            print(f"Error いいねの確認処理失敗: {e}")
            return jsonify({'error': 'Failed to query existing like'}), 500
        
        if existing_like:
            try:
                # すでに「いいね」している場合は削除
                db.session.delete(existing_like)
                db.session.commit()
            except Exception as e:
                print(f"Error いいねの削除失敗: {e}")
                return jsonify({'error': 'Failed to remove like'}), 500
            action = 'removed'
        else:
            try:
                # 新たに「いいね」を追加
                new_like = Like(userId=user_id, saleId=sale_id)
                db.session.add(new_like)
                db.session.commit()
            except Exception as e:
                print(f"Error いいね追加失敗: {e}")
                return jsonify({'error': 'Failed to add like'}), 500
            action = 'added'
        
        try:
            # 「いいね」された商品に対する「いいね」の数を取得
            like_count = Like.query.filter_by(saleId=sale_id).count()
        except Exception as e:
            print(f"Error いいね数の取得失敗: {e}")
            return jsonify({'error': 'Failed to query like count'}), 500
        
        print(f"Like count for sale {sale_id}: {like_count}")
        return jsonify({'action': action, 'likeCount': like_count})
