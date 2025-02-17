from imports import *
from auth.config import ENVIRONMENT
from auth.azure_blob import connect_to_azure_blob
from auth.img_helper import *

def add_sale(app):
    # MARK:　出品ページ
    @app.route('/add_sale', methods=['POST'])
    def add_sale_view():
        try:
            data = request.get_json()
            image_data = data.get('image')
            time = data.get('time')
            price = data.get('price')
            title = data.get('title')
            postingTime = data.get('postingTime')
            categories = data.get("categories")
            print(title)
            print(postingTime)
            print(categories)
        except Exception as e:
            print(f"Error 出品情報取得失敗: {e}")
            return jsonify({'error': 'Failed to parse request data'}), 400
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400

        image_bytes = decode_image(image_data)
        if not image_bytes:
            return jsonify({'error': 'Invalid image data'}), 400

        if ENVIRONMENT == 'local':
            # 画像をローカルフォルダに保存
            file_path = save_image_to_file(image_bytes, app.config['UPLOAD_FOLDER'])
            file_path = file_path.replace(app.config['UPLOAD_FOLDER'], 'upload_images')
        else:
            try:
                # 画像をAzure Blob Storageに保存
                blob_url = save_image_to_azure(image_bytes)
                if not blob_url:
                    return jsonify({"error": "Failed to save image"}), 500
            except Exception as e:
                # 保存成功時に画像のURLを返す
                return jsonify({"message": "Image uploaded successfully", "image_url": blob_url}), 201


        userId = session.get('userId') # 今使っているユーザーのuserIdの取得
        try:
            user = User.query.get(userId) # userIdからuser情報受け取り
        except Exception as e:
            print(f"Error ユーザー情報取得失敗: {e}")
            return jsonify({'error': 'Failed to query user'}), 500
        
        displayName = user.displayName # displayNameの取得

        #現在時刻取得
        dt = datetime.now()
        datetimeStr = dt.strftime('%Y/%m/%d %H:%M:%S')
        #掲載時間計算
        postingTimePlus = dt + timedelta(minutes=int(postingTime))
        postingTimeStr = postingTimePlus.strftime('%Y/%m/%d %H:%M:%S')
        print("現在時刻：", datetimeStr)
        print("掲載満了時刻：", postingTimeStr)

        try:
            new_sale = Sale(userId=userId, displayName=displayName, title=title, filePath=file_path, startingPrice=price,currentPrice=price, creationTime=time, startingTime=datetimeStr, finishTime=postingTimeStr)
            
            # categories 変数の値に基づいて Category を一度に取得
            category_objects = Category.query.filter(Category.categoryName.in_(categories)).all()
            db.session.add(new_sale)
            db.session.commit()
        except Exception as e:
            print(f"Error 出品処理失敗: {e}")
            return jsonify({'error': 'Failed to create sale'}), 500
        
    

        # 存在しないカテゴリ名のチェック
        found_category_names = {category.categoryName for category in category_objects}
        missing_categories = set(categories) - found_category_names
        if missing_categories:
            # ログを出力するか、エラー処理を追加
            print(f"Warning: The following categories were not found: {missing_categories}")

        try:
            # 中間テーブルにカテゴリーを追加
            new_sale.categories.extend(category_objects)
            new_bid = Bid(userId=userId, saleId=new_sale.saleId, bidPrice=price)
            db.session.add(new_sale, new_bid)
            db.session.commit()
        except Exception as e:
            print(f"Error 中間テーブルへの追加失敗: {e}")
            return jsonify({'error': 'Failed to add categories'}), 500

        return jsonify({'message': 'Sale added successfully'}), 201    
