from imports import *
from auth.config import UPLOAD_STORAGE
from auth.azure_blob import connect_to_azure_blob
from auth.img_helper import *
import pytz
import sys
import base64

def add_sale(app):
    
    @app.route('/get_category_name', methods=['POST'])
    def get_category_name():
        try:
            # フロントエンドから送られてきたcategoryIdを取得
            data = request.get_json()
            category_id = data.get('categoryId')

            # categoryIdを使ってカテゴリ名を取得
            category = Category.query.filter_by(categoryId=category_id).first()

            if category:
                # カテゴリが見つかった場合、カテゴリ名を返す
                return jsonify({'categoryName': category.categoryName})
            else:
                # カテゴリが見つからない場合
                return jsonify({'error': 'Category not found'}), 404

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({'error': 'Failed to fetch category name'}), 500
        
    # MARK:　出品ページ
    @app.route('/add_sale', methods=['POST'])
    @login_required
    def add_sale_view():
        try:
            data = request.get_json()
            title = data.get('title')
            postingTime = data.get('postingTime')
            image_data = data.get('image')
            time = data.get('time')
            price = data.get('price')
            kategori = data.get('kategori')

            print(title)
            print(postingTime)
            print(kategori)

            # カテゴリIDを使ってカテゴリ情報を取得
            category = Category.query.filter_by(categoryId=kategori).first()

            if not category:
                return jsonify({'error': 'Category not found'}), 400

            # カテゴリ名を表示（デバッグ用）
            print(f"選択されたカテゴリ名: {category.categoryName}")

        except Exception as e:
            print(f"Error 出品情報取得失敗: {e}")
            return jsonify({'error': 'Failed to parse request data'}), 400
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        # Base64デコードの処理を明示的に記述
        if image_data.startswith("data:image/png;base64,"):
            image_data = image_data.replace("data:image/png;base64,", "")

        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            print(f"Error: Base64 decoding failed - {e}")
            return jsonify({'error': 'Invalid image data'}), 400

        if UPLOAD_STORAGE == 'local':
            # 画像をローカルフォルダに保存
            file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])
            file_path = file_path.replace(app.config['UPLOAD_FOLDER'], 'upload_images')
        else:
            try:
                # 画像をAzure Blob Storageに保存
                file_path = save_image_to_azure(image_bytes)
                if not file_path:
                    return jsonify({"error": "Failed to save image"}), 500
            except Exception as e:
                # 保存成功時に画像のURLを返す
                return jsonify({"message": "Image uploaded successfully", "image_url": file_path}), 201


        userId = session.get('userId') # 今使っているユーザーのuserIdの取得
        try:
            user = db.session.query(User).get(userId)  # userIdからuser情報受け取り
        except Exception as e:
            print(f"Error ユーザー情報取得失敗: {e}")
            return jsonify({'error': 'Failed to query user'}), 500
        
        displayName = user.displayName # displayNameの取得

        #現在時刻取得
        dt = datetime.now(pytz.timezone('Asia/Tokyo'))
        datetimeStr = dt.strftime('%Y/%m/%d %H:%M:%S')
        #掲載時間計算
        postingTimePlus = dt + timedelta(minutes=int(postingTime))
        postingTimeStr = postingTimePlus.strftime('%Y/%m/%d %H:%M:%S')
        print("現在時刻：", datetimeStr, file=sys.stderr)
        print("掲載満了時刻：", postingTimeStr, file=sys.stderr)

        try:
            new_sale = Sale(userId=userId, displayName=displayName, title=title, filePath=file_path, startingPrice=price,currentPrice=price, creationTime=time, startingTime=datetimeStr, finishTime=postingTimeStr)
            db.session.add(new_sale)
            db.session.commit()
        except Exception as e:
            print(f"Error 出品処理失敗: {e}")
            return jsonify({'error': 'Failed to create sale'}), 500

        try:
            # 新しいビッドを作成
            new_bid = Bid(userId=userId, saleId=new_sale.saleId, bidPrice=price)
            db.session.add(new_sale, new_bid)
            db.session.commit()
        except Exception as e:
            print(f"Error ビッド処理失敗: {e}")
            return jsonify({'error': 'Failed to add bid'}), 500

        try:
            # 中間テーブルにカテゴリ関連を追加
            new_association = saleCategoryAssociation.insert().values(saleId=new_sale.saleId, categoryId=kategori)
            db.session.execute(new_association)
            db.session.commit()
        except Exception as e:
            print(f"Error 中間テーブルへの追加失敗: {e}")
            return jsonify({'error': 'Failed to associate sale with category'}), 500

        # 出品成功メッセージ
        return jsonify({'message': 'Sale added successfully'}), 201  
    